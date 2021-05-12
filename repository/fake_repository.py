from uuid import UUID
from typing import Iterable

from repository.repository import Repository

_bank_a = UUID("111aaaaa-1af0-489e-b761-d40344c12e70")
_bank_b = UUID("222aaaaa-1af0-489e-b761-d40344c12e70")
_bank_g = UUID("333aaaaa-1af0-489e-b761-d40344c12e70")

_oleg = "bd2e86ce81ae00d65c2c02074a1e85c0a483613c74760f22f1fc07080d6e5dc5"
_olga = "9c2d29850e7fd884c19b3ef48a01b82c0a88854082ad150056ac770dcbeee05c"
_kate = "1a5d06a170dde413475957ca2b63396aa5e8fbecb7d379fcb668da3753fca5b6"
_john = "a8cfcd74832004951b4408cdb0a5dbcd8c7e52d43f7fe244bf720582e05241da"
_inga = "16269daaef0fcf94c6394f7c2cdecdf99f44c96d3c3fdd8b3b53b46a52d47821"
_dave = "809a721743350c0c49a7b444ad3aeaf1341fdd48d1bf510e08b008edab72dc70"
_tony = "c5a8d95238cd3ee8c28a86b7ef8553a7c27ac016577c7717b52c69fa4f721b7f"
_jane = "4f23798d92708359b734a18172c9c864f1d48044a754115a0d4b843bca3a5332"

_clients = {
    _bank_a: {
        _oleg: 199,
        _olga: 102,
        _kate: 403,
        _john: -296,
        _inga: 605,
        _dave: 1000000,
    },
    _bank_b: {
        _oleg: -500,
        _olga: 600,
        _kate: -100,
        _john: 400,
        _inga: 200,
        _tony: -900000
    },
    _bank_g: {
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

    def get_balances(self, clients: Iterable[str]) -> Iterable[int]:
        return [self._get_balance(client) for client in clients]

    def _get_balance(self, client_hash: str) -> int:
        try:
            if not isinstance(client_hash, str):
                raise TypeError
            return _clients[self.uuid][client_hash]
        except KeyError:
            return 0
