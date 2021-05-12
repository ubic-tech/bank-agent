from uuid import UUID
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from pymotyc import Engine, Collection, errors
from models.common import Shares
from config import config
from utils.decompose import modulo_transform

_engine = Engine()
_motor = AsyncIOMotorClient(config.MONGO_HOST, config.MONGO_PORT)
_tid = "transaction_id"


class TransactionExists(Exception):
    pass


class ShareAlreadyReceived(Exception):
    pass


class NotSinglePartnerShare(Exception):
    pass


class MongoModel(BaseModel):
    pass


class PartnerShare(MongoModel):
    partner_id: UUID
    shares: Optional[Shares]
    received: int


class TransactionInfo(MongoModel):
    transaction_id: UUID
    num_partners: int
    partner_shares: List[PartnerShare]


@_engine.database
class Transactions:
    transactions: Collection[TransactionInfo]


async def create_transaction_manager(
        motor: Optional[AsyncIOMotorClient] = None):
    await _engine.bind(motor=_motor if motor is None else motor,
                       inject_motyc_fields=True)
    await Transactions.transactions.collection.drop()
    await Transactions.transactions.collection.create_index(_tid, unique=True)


class TransactionManager:
    @staticmethod
    async def add_transaction(transaction_id: UUID,
                              partners: [UUID],
                              my_share: Shares):
        try:  # assert not exists
            await Transactions.transactions.find_one(
                {_tid: transaction_id}
            )
            raise TransactionExists()
        except errors.NotFound:
            pass
        init_partner_shares = [
            PartnerShare(
                partner_id=UUID(config.BANK_UUID),
                shares=my_share.copy(),
                received=1
            ), *[
                PartnerShare(partner_id=p,
                             shares=[0 for _ in range(len(my_share))],
                             received=0)
                for p in partners if p != UUID(config.BANK_UUID)
            ]
        ]
        tr_info = TransactionInfo(
            transaction_id=transaction_id,
            num_partners=len(partners),
            partner_shares=init_partner_shares
        )
        await Transactions.transactions.save(tr_info)

    @staticmethod
    async def add_partner_share(transaction_id: UUID,
                                partner_id: UUID,
                                shares: Shares):
        tran = await TransactionManager._get_transaction(transaction_id)
        if tran is None:
            return
        partner_indices = [
            i for i, partner in enumerate(tran.partner_shares)
            if partner.partner_id == partner_id
        ]
        if len(partner_indices) != 1:  # exactly 1 PartnerShare from each partner is expected
            raise NotSinglePartnerShare  # already in db, no use to inc

        partner_index = partner_indices[0]
        invalidate: bool = tran.partner_shares[partner_index].received != 0

        # each value from received shares to each field in db's partner_shares
        update_data = {f"partner_shares.{partner_index}.shares.{ind}": val
                       for ind, val in enumerate(shares)}
        update_data[f"partner_shares.{partner_index}.received"] = 1  # set received flag through inc

        await Transactions.transactions.collection.update_one(
            {_tid: transaction_id}, {"$inc": update_data}
        )
        if invalidate:
            raise ShareAlreadyReceived(partner_id)

    @staticmethod
    async def get_shares_if_ready(transaction_id: UUID) -> Optional[Shares]:
        transaction = await TransactionManager._get_transaction(transaction_id)
        if transaction is None:
            return None
        received = sum(
            1 for p_sh in transaction.partner_shares if p_sh.received == 1
        )
        if received != transaction.num_partners:
            return None
        shares = [p_sh.shares for p_sh in transaction.partner_shares]
        column_sums = [modulo_transform(sum(i)) for i in zip(*shares)]
        return column_sums

    @staticmethod
    async def find(transaction_id: UUID):
        return await TransactionManager._get_transaction(transaction_id) is not None

    @staticmethod
    async def _get_transaction(transaction_id: UUID) -> Optional[TransactionInfo]:
        try:
            transaction = await Transactions.transactions.find(
                {_tid: transaction_id}
            )  # throws DuplicateKeyError if not single
            try:
                return transaction[0]
            except IndexError:   # means no such a transaction at all
                return None
        except DuplicateKeyError:
            return None
