from uuid import UUID

from repository.fake_repository import FakeRepository


def test_fake_repository():
    rep = FakeRepository(UUID("111aaaaa-1af0-489e-b761-d40344c12e70"))
    clients = [UUID("aaa1fc87-5722-4383-9830-2be483b6468d"),
               "aaa1fc87-5722-4383-9830-2be483b6468d",
               UUID("6661fc87-5722-4383-9830-2be483b6468d"), ]
    assert rep.get_balances(clients) == [199, 199, 0]


if __name__ == '__main__':
    test_fake_repository()
