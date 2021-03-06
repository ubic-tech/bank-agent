from abc import ABC, abstractmethod
from typing import Any, Mapping, cast, Type, Union

from pydantic import BaseModel
from pydantic.fields import ModelField
from typing_extensions import Literal

CompareOp = Literal['__eq__', '__gt__', '__ge__', '__lt__', '__le__', '__ne__']

compare_ops_repr: Mapping[CompareOp, str] = cast(
    Mapping[CompareOp, str],
    {'__eq__': '==', '__gt__': '>', '__ge__': '>=', '__lt__': '<', '__le__': '<=', '__ne__': '!='})

compare_ops_mongo: Mapping[CompareOp, str] = cast(
    Mapping[CompareOp, str],
    {'__eq__': '$eq', '__gt__': '$gt', '__ge__': '$gte', '__lt__': '$lt', '__le__': '$lte', '__ne__': '$ne'})

LogicalOp = Literal['__and__', '__or__']

logical_ops_repr: Mapping[LogicalOp, str] = cast(
    Mapping[LogicalOp, str],
    {'__and__': 'AND', '__or__': 'OR'})

logical_ops_mongo: Mapping[LogicalOp, str] = cast(
    Mapping[LogicalOp, str],
    {'__and__': '$and', '__or__': '$or'})

MongoQuery = dict


# ====================================================

class MotycQuery(ABC):
    def __and__(self, other: 'MotycQuery'):
        return MotycQueryNode(self, '__and__', other)

    def __or__(self, other: 'MotycQuery'):
        return MotycQueryNode(self, '__or__', other)

    @abstractmethod
    def to_mongo_query(self) -> MongoQuery:
        ...

    @staticmethod
    def build_mongo_query(query: Union[dict, 'MotycQuery']) -> dict:
        """ Builds MongoDB query from MotycQuery or dict, where keys can be MotycFields.

        :param query: Query, built with MoticQuery builder or dict with raw MongoDB query,
            where keys can be not only string, but also MotycFields (typically injected).
        :return: Raw MongoDB query.
        """

        if isinstance(query, MotycQuery):
            return query.to_mongo_query()

        assert isinstance(query, dict)

        def mod_requrs(query: Union[dict, Any]) -> dict:
            if not isinstance(query, dict): return query
            result = {}
            for key, val in query.items():
                if isinstance(key, MotycField):
                    key = key.model_field.alias

                if isinstance(val, list):
                    val = [mod_requrs(item) for item in val]
                elif isinstance(val, dict):
                    val = mod_requrs(val)

                result[key] = val
            return result

        return mod_requrs(query)


# ====================================================

class MotycQueryLeaf(MotycQuery, ABC):

    def __init__(self, motyc_field: 'MotycField'):
        self.motyc_field = motyc_field


# ----------------------------------------------------

class MotycQueryLeafCompare(MotycQueryLeaf):

    def __init__(self, motyc_field: 'MotycField', op: CompareOp, literal: Any):
        super().__init__(motyc_field)
        self.op = op
        self.literal = literal

    def __str__(self):
        return f"{self.motyc_field.model_field.alias}{compare_ops_repr[self.op]}{self.literal}"

    def to_mongo_query(self) -> MongoQuery:
        return {self.motyc_field.model_field.alias: {compare_ops_mongo[self.op]: self.literal}}


# ----------------------------------------------------


class MotycQueryLeafRegex(MotycQueryLeaf):
    def __init__(self, motyc_field: 'MotycField', pattern: str, options: str):
        super().__init__(motyc_field)
        self.pattern = pattern
        self.options = options

    def __str__(self):
        return f"{self.motyc_field.model_field.alias}~=/{self.pattern}/{self.options}"

    def to_mongo_query(self) -> MongoQuery:
        return {self.motyc_field.model_field.alias: {"$regex": self.pattern, "$options": self.options}}


# ====================================================

class MotycQueryNode(MotycQuery):
    def __init__(self, left: MotycQuery, op: LogicalOp, right: MotycQuery):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.left} {logical_ops_repr[self.op]} {self.right})"

    def to_mongo_query(self) -> MongoQuery:
        return {logical_ops_mongo[self.op]: [self.left.to_mongo_query(), self.right.to_mongo_query()]}


# ====================================================


class MotycField():
    def __init__(self, model_field: ModelField):
        self.model_field = model_field

    def __eq__(self, other):
        return MotycQueryLeafCompare(self, '__eq__', other)

    def __gt__(self, other):
        return MotycQueryLeafCompare(self, '__gt__', other)

    def __ge__(self, other):
        return MotycQueryLeafCompare(self, '__ge__', other)

    def __lt__(self, other):
        return MotycQueryLeafCompare(self, '__lt__', other)

    def __le__(self, other):
        return MotycQueryLeafCompare(self, '__le__', other)

    def __ne__(self, other):
        return MotycQueryLeafCompare(self, '__ne__', other)

    def regex(self, pattern: str, options: str = ""):
        return MotycQueryLeafRegex(self, pattern, options)

    def __hash__(self):
        return hash(self.model_field.alias)

    @staticmethod
    def _inject_for_model(model: Type[BaseModel]):
        field: ModelField
        for field_name, field in model.__fields__.items():
            if isinstance(field, ModelField):
                setattr(model, field_name, MotycField(field))


# noinspection PyPep8Naming
def M(motyc_field: Any) -> MotycField:
    return cast(MotycField, motyc_field)
    # assert isinstance(motyc_field, MotycField)
    # return motyc_field
