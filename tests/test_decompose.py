from utils.decompose import decompose, modulo_transform
from config import config


def test_decompose():
    parts_number = 500
    for secret in [-100, 100, 100339, -9723892]:
        decomposed = decompose(secret, parts_number)
        restored = modulo_transform(sum(decomposed))
        if restored > config.MODULO/2:
            restored -= config.MODULO
        elif restored < -config.MODULO/2:
            restored += config.MODULO
        assert len(decomposed) == parts_number
        assert restored == secret, (secret, restored)


if __name__ == '__main__':
    test_decompose()
