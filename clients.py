from uuid import UUID

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


class Repository:
    def __init__(self, uuid: UUID):
        self.uuid = uuid

    def get_balance(self, client_uuid) -> int:
        try:
            if isinstance(client_uuid, UUID):
                return _clients[self.uuid][client_uuid]
            elif isinstance(client_uuid, str):
                return _clients[self.uuid][UUID(client_uuid)]
            else:
                raise TypeError
        except KeyError:
            return 0


if __name__ == '__main__':
    rep = Repository(UUID("111aaaaa-1af0-489e-b761-d40344c12e70"))
    assert rep.get_balance(UUID("aaa1fc87-5722-4383-9830-2be483b6468d")) == 200
    assert rep.get_balance("aaa1fc87-5722-4383-9830-2be483b6468d") == 200
    assert rep.get_balance(UUID("6661fc87-5722-4383-9830-2be483b6468d")) == 0
