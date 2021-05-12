from uuid import UUID

from models.common import Shares
from tests.ubic_stub import transaction_manager as transactions


def test_transaction_info():
    partners_count = 3
    num_clients = 5
    incoming_shares: Shares = [
        [1, 2, 3, 4, 5, ],
        [10, 20, 30, 40, 50, ],
        [100, 200, 300, 400, 500, ],  # from partner N
    ]
    expected = [111, 222, 333, 444, 555]

    ti = transactions.TransactionInfo(partners_count, num_clients)
    for incoming in incoming_shares:
        assert ti.ready() is False
        ti.sum_up(incoming)

    assert ti.ready() is True
    assert expected == ti.get_shares()
    shares = ti.get_shares()
    shares[0] = 100500
    assert expected == ti.get_shares()


def test_transaction_manager():
    transaction_id = UUID("111aaaaa-1af0-489e-b761-d40344c12e70")
    partners_count = 3
    num_clients = 5
    incoming_shares: Shares = [
        [1, 2, 3, 4, 5, ],
        [10, 20, 30, 40, 50, ],
        [100, 200, 300, 400, 500, ],  # from partner N
    ]
    expected = [111, 222, 333, 444, 555]

    transaction_manager = transactions.TransactionManager()

    transaction_manager.add(transaction_id, partners_count, num_clients)

    for incoming in incoming_shares:
        assert transaction_manager.ready(transaction_id) is False
        transaction_manager.sum_up(transaction_id, incoming)

    assert transaction_manager.ready(transaction_id)
    assert expected == transaction_manager.get_shares(transaction_id)
    shares = transaction_manager.get_shares(transaction_id)
    shares[0] = 100500
    assert expected == transaction_manager.get_shares(transaction_id)


if __name__ == '__main__':
    test_transaction_info()
    test_transaction_manager()
