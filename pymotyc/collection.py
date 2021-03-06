from typing import TypeVar, Generic, List, Optional, Union, Type, Iterable, Callable, cast
from uuid import uuid4

import typing_inspect
from motor.core import AgnosticCollection, AgnosticDatabase, AgnosticCursor
from pydantic import parse_obj_as, BaseModel
from pymongo import IndexModel
from pymongo.results import InsertOneResult, UpdateResult

from pymotyc import Engine
from pymotyc.errors import NotFound
from pymotyc.query import MotycQuery, MotycField

T = TypeVar('T')


class Collection(Generic[T]):
    class Identity:
        ...

    # Motor collection.
    collection: AgnosticCollection

    # Motor database.
    db: AgnosticDatabase

    # Type of the collection, should be BaseModel or Union of them.
    # Untyped collections (as well as typed with simple dict) not supported yet.
    t: type

    def __init__(
            self, *,
            name: Optional[str] = None,
            identity: str = '_id',
            indexes: Iterable[Union[str, IndexModel]] = (),
            id_generator: Callable = lambda: str(uuid4())
    ):
        """ Initializes Collection instance.
        :param name: Collection name, if None will be set during engine binding to name of attriute of database.
        :param identity: Document's field name, which represents identity:
            - If '_id' or None - default identity management through MongoDB _id field is implied, so if this field
                is None or absent in the document to save - document inserted, otherwise upsered based on '_id' field.
            - If other - documents always upserted based on this field, if no or None - will be generated by _generate_id().
                If default '_id' is presented in the document - it's ignored while saving.
                Please note, if model field is used with alias, the alias, not model field name should be provided there!
                This is especially true for default MongoDB _id field, you can not name field in model with '_id',
                due to Pydantic limitations, so alias should be used.
        :param indexes: Collection indexes to create, can be field name or composite MongoDB index??
            - items which are str created with MotorCollection.create_index(),
            - items which are IndexModel created with MotorCollection.create_indexes(), so additional
                params like unique = True can be provided in the model.

            For non-default identity field, unique index is always created.

            Indexes are created during colleciton binding, so if collection dropped after that,
            indexes should be re-recreated manually by calling Collection.create_indexes().

        :param id_generator: Callable to generate id for non-default identity management.
        """
        self.name = name
        self.identity = identity
        self.indexes = indexes
        self.id_generator = id_generator

    async def save(
            self, item: T, *,
            force_default_id: bool = None
    ) -> T:
        assert isinstance(item, BaseModel), "Can only handle BaseModel, not dict i.g."

        # We'll parse item first, to be sure it corresponds collection schema
        document = parse_obj_as(cast(Type[T], self.t), item.dict(by_alias=True)).dict(by_alias=True)

        # special case: model has no _id, but it forced by force_default_id=True in other methods
        if '_id' not in document and hasattr(item, '_id'): document['_id'] = item._id

        if self.identity is None or self.identity == '_id':
            if document.get('_id') is None:
                if '_id' in document: del document['_id']
                result: InsertOneResult = await self.collection.insert_one(document)
                document['_id'] = result.inserted_id
            else:
                result: UpdateResult = await self.collection.update_one(
                    {'_id': document['_id']},
                    {'$set': document}, upsert=True
                )
                if result.upserted_id is not None:
                    assert result.upserted_id == document['_id'], "Should be equal, please report if no."

        elif isinstance(self.identity, str):
            assert not force_default_id, "Force_default_id is not supported with non-default identity."
            if document.get(self.identity) is None:
                document[self.identity] = self.generate_id()

            if '_id' in document: del document['_id']

            _result: UpdateResult = await self.collection.update_one(
                {self.identity: document[self.identity]},
                {'$set': document}, upsert=True
            )
        else:
            assert False, "Unknown identity type."

        model = self._parse_document(document, force_default_id=force_default_id)

        return model

    async def find_one(
            self, query: Union[dict, MotycQuery] = None, *,
            force_default_id: bool = None
    ) -> T:
        document = await self.collection.find_one(self._build_mongo_query(query))
        if document is None: raise NotFound()
        return self._parse_document(document, force_default_id=force_default_id)

    async def find(
            self, query: Union[dict, MotycQuery] = None, *,
            sort: dict = None,  # todo: MotycField?
            limit: int = None,
            force_default_id: bool = None,
    ) -> List[T]:
        cursor: AgnosticCursor = self.collection.find(self._build_mongo_query(query))
        if sort is not None: cursor = cursor.sort([(k, v) for k, v in sort.items()])
        result = []
        async for document in cursor:
            if limit is not None and len(result) >= limit: break
            result.append(self._parse_document(document, force_default_id=force_default_id))
        return result

    async def create_indexes(self):
        if self.identity != '_id':
            await self.collection.create_index(self.identity, unique=True)

        if self.indexes: await self.collection.create_indexes([
            i if isinstance(i, IndexModel) else IndexModel(i)
            for i in self.indexes
        ])

    def generate_id(self):
        # todo config in engine
        assert self.identity != '_id', 'Supported only for non default id field'
        return self.id_generator()

    # ----------------------------------------------------

    # noinspection PyUnusedLocal
    async def _bind(
            self, engine: Engine, db: AgnosticDatabase, t: type, name: str, *,
            inject_motyc_fields=False,
    ):

        models = Collection._check_type_get_basemodels(t)

        self.t = t
        self.db = db
        if self.name is None: self.name = name
        self.collection = getattr(db, self.name)

        if inject_motyc_fields:
            for model in models: MotycField._inject_for_model(model)

    # ----------------------------------------------------

    def _build_mongo_query(self, query: Union[dict, MotycQuery] = None):
        return MotycQuery.build_mongo_query(query)

    def _parse_document(self, document: dict, *, force_default_id: bool = False) -> T:
        model = parse_obj_as(cast(Type[T], self.t), document)
        if force_default_id: object.__setattr__(model, '_id', document.get('_id', None))
        if hasattr(model, '_bound_collection'): model._bound_collection = self
        return model

    @staticmethod
    def _check_type_get_basemodels(t: type) -> List[Type[BaseModel]]:
        """ Checks if collection type is subclass of BaseModel or Union of them, returns list of BaseModels involved.
        In future untyped collection or Colelction[dict] will be supported.
        :param t: Type of collection.
        :return: List of BaseModels, which collection can hold.
        :raise: TypeError if collection type is improper.
        """
        result = []
        if typing_inspect.is_union_type(t):
            for tt in typing_inspect.get_args(t):
                if not issubclass(tt, BaseModel):
                    raise TypeError(f"Args of Union must be BaseModels, {t} not.")
                result.append(tt)
        else:
            try:
                if issubclass(t, BaseModel): result.append(t)
            except TypeError:
                pass

        from pymotyc import MotycModel
        for tt in [*result]:
            for parent in tt.__mro__:
                if parent in [MotycModel, BaseModel]: break
                if parent not in result: result.append(parent)

        if not result: raise TypeError(f"Improper type {t} of the Collection.")

        return result
