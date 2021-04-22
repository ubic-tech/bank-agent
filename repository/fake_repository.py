from uuid import UUID
from typing import Iterable

from repository.repository import Repository

_oleg = UUID("aaa1fc87-5722-4383-9830-2be483b6468d")
_olga = UUID("bbb1fc87-5722-4383-9830-2be483b6468d")
_kate = UUID("ccc1fc87-5722-4383-9830-2be483b6468d")
_john = UUID("ddd1fc87-5722-4383-9830-2be483b6468d")
_inga = UUID("eee1fc87-5722-4383-9830-2be483b6468d")
_dave = UUID("a1a1fc87-5722-4383-9830-2be483b6468d")
_tony = UUID("b2b1fc87-5722-4383-9830-2be483b6468d")
_jane = UUID("c3c1fc87-5722-4383-9830-2be483b6468d")

_clients = {
    UUID("111aaaaa-1af0-489e-b761-d40344c12e70"): {
        _oleg: 199,
        _olga: 102,
        _kate: 403,
        _john: -296,
        _inga: 605,
        _dave: 1000000,
    },
    UUID("222aaaaa-1af0-489e-b761-d40344c12e70"): {
        _oleg: -500,
        _olga: 600,
        _kate: -100,
        _john: 400,
        _inga: 200,
        _tony: -900000
    },
    UUID("333aaaaa-1af0-489e-b761-d40344c12e70"): {
        _oleg: 200,
        _olga: -100,
        _kate: 300,
        _john: 500,
        _inga: -100,
        _jane: 100500,
    }
}


class FakeRepository(Repository):
    def __init__(self, uuid: UUID):
        self.uuid = uuid

    def get_balances(self, clients: Iterable[UUID]) -> Iterable[int]:
        return [self._get_balance(client) for client in clients]

    def _get_balance(self, client_uuid) -> int:
        try:
            if isinstance(client_uuid, UUID):
                return _clients[self.uuid][client_uuid]
            elif isinstance(client_uuid, str):
                return _clients[self.uuid][UUID(client_uuid)]
            else:
                raise TypeError
        except KeyError:
            return 0


def test():
    rep = FakeRepository(UUID("111aaaaa-1af0-489e-b761-d40344c12e70"))
    clients = [UUID("aaa1fc87-5722-4383-9830-2be483b6468d"),
               "aaa1fc87-5722-4383-9830-2be483b6468d",
               UUID("6661fc87-5722-4383-9830-2be483b6468d"), ]
    assert rep.get_balances(clients) == [199, 199, 0]


if __name__ == '__main__':
    test()
