import subprocess
import os
import asyncio
from uuid import UUID, uuid4
import pytest

from transaction_manager import (
    create_transaction_manager,
    AsyncIOMotorClient,
    TransactionManager,
    TransactionExists,
    ShareAlreadyReceived
)

MONGO_MOCK_HOST = "localhost"
MONGO_MOCK_PORT = 37017
MONGO_MOCK_NAME = "mongo_db_mock"

me = UUID("111aaaaa-1af0-489e-b761-d40344c12e70")
partner1 = UUID("222aaaaa-1af0-489e-b761-d40344c12e70")
partner2 = UUID("333aaaaa-1af0-489e-b761-d40344c12e70")
shares = {
    me: [1, 2, 3, 4, 5],
    partner1: [10, 20, 30, 40, 50],
    partner2: [100, 200, 300, 400, 500],
}
total = [111, 222, 333, 444, 555]


async def positive(manager: TransactionManager):
    tid = uuid4()
    assert await manager.find(tid) is False
    await manager.add_transaction(
        transaction_id=tid,
        partners=[me, partner1, partner2],
        my_share=shares[me]
    )
    assert await manager.find(tid)
    for partner, share in shares.items():
        assert await manager.get_shares_if_ready(tid) is None
        if partner == me:
            continue
        await manager.add_partner_share(
            transaction_id=tid,
            partner_id=partner,
            shares=share
        )
    assert await manager.get_shares_if_ready(tid) == total


async def negative(manager: TransactionManager):
    tid = uuid4()
    await manager.add_transaction(
        transaction_id=tid,
        partners=[me, partner1, partner2],
        my_share=shares[me]
    )

    try:
        await manager.add_transaction(
            transaction_id=tid,
            partners=[me, partner1, partner2],
            my_share=shares[me]
        )
        assert False, "TransactionExists is expected"
    except TransactionExists:
        pass

    for partner, share in shares.items():
        assert await manager.get_shares_if_ready(tid) is None
        if partner == me:
            continue
        await manager.add_partner_share(
            transaction_id=tid,
            partner_id=partner,
            shares=share
        )
    try:
        await manager.add_partner_share(
            transaction_id=tid,
            partner_id=partner1,
            shares=shares[partner1]
        )
        assert False, "ShareAlreadyReceived is expected"
    except ShareAlreadyReceived:
        pass
    assert await manager.get_shares_if_ready(tid) is None


@pytest.mark.asyncio
async def test():
    mongo_up_cmd = f"docker run -d -p {MONGO_MOCK_PORT}:27017"\
                   f" --name {MONGO_MOCK_NAME} mongo:4.0.4"
    try:
        subprocess.check_call(mongo_up_cmd, shell=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        assert False, f"Failed to create mongo mock. Make sure port {MONGO_MOCK_PORT}"\
                      f" is vacant and no container named {MONGO_MOCK_NAME} running. Or reconfigure tests"
    test_motor = AsyncIOMotorClient(
        MONGO_MOCK_HOST,
        MONGO_MOCK_PORT,
        io_loop=asyncio.get_event_loop()
    )
    await create_transaction_manager(motor=test_motor)
    manager = TransactionManager()
    await positive(manager)
    await negative(manager)
    os.system(f"docker rm -f {MONGO_MOCK_NAME}")
