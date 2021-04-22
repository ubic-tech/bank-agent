import abc
from uuid import UUID
from typing import Iterable


class Repository(abc.ABC):
    @abc.abstractmethod
    def get_balances(self, clients: Iterable[UUID]) -> Iterable[int]:
        raise NotImplementedError
