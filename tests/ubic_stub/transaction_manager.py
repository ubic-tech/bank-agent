from uuid import UUID
from multiprocessing import Lock

from models.common import Shares
from config import config


def modulo_transform(value: int) -> int:
    value %= config.MODULO
    if value > config.SEMI_MODULO:
        return value - config.MODULO
    elif value < -config.SEMI_MODULO:
        return value + config.MODULO
    else:
        return value


class TransactionInfo:
    def __init__(self, partners_count: int, num_clients: int):
        self.partners_count = partners_count
        self.shares_received = 0
        self.shares = [0 for _ in range(num_clients)]

    def sum_up(self, shares: Shares):
        assert isinstance(shares, (Shares, list))
        assert self.shares_received != self.partners_count
        self.shares = [modulo_transform(x+y) for (x, y) in zip(shares, self.shares)]
        self.shares_received += 1

    def ready(self) -> bool:
        return self.shares_received == self.partners_count

    def get_shares(self) -> Shares:
        return self.shares.copy()


class TransactionManager:
    def __init__(self):
        self.transactions: {UUID: TransactionInfo} = {}
        self.mtx = Lock()

    def add(self, transaction_id: UUID, partners_count: int, num_clients: int):
        with self.mtx:  # create if not exists, secure access required for clean writing
            if transaction_id not in self.transactions:
                self.transactions[transaction_id] = TransactionInfo(
                    partners_count, num_clients
                )
            else:
                raise Exception("already exists")

    def sum_up(self, transaction_id: UUID, shares: Shares) -> Shares:
        with self.mtx:
            self.transactions[transaction_id].sum_up(shares)

    def ready(self, transaction_id: UUID) -> bool:
        with self.mtx:
            return self.transactions[transaction_id].ready()

    def get_shares(self, transaction_id: UUID) -> Shares:
        with self.mtx:
            if not self._find(transaction_id):
                raise KeyError
            return self.transactions[transaction_id].get_shares()

    def find(self, transaction_id: UUID) -> bool:
        with self.mtx:
            return self._find(transaction_id)

    def _find(self, transaction_id: UUID) -> bool:
        return self.transactions.get(transaction_id) is not None
