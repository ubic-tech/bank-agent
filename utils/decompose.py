from random import randrange, randint

from config import config


def modulo_transform(value: int) -> int:
    value %= config.MODULO
    if value > config.SEMI_MODULO:
        return value - config.MODULO
    elif value < -config.SEMI_MODULO:
        return value + config.MODULO
    else:
        return value


def get_rand_pair(secret: int) -> (int, int):
    """
    return a pair of random integers so that their sum % MODULO == secret
    :param secret: integer to be split into 2 shares
    :return: a pair of base's components
    """
    assert secret < config.MODULO, f"{secret} > {config.MODULO}"
    share0 = randrange(config.MODULO)
    share1 = modulo_transform(secret - share0)
    return share0, share1


def decompose(secret: int, parts_count: int) -> [int]:
    """
    :param secret: integer to be split into N shares
    :param parts_count: how many shares to return
    :return: list of components so that their sum % MODULO == secret
    """
    assert parts_count >= config.MIN_PARTNERS_NUM
    res = []
    res.extend(get_rand_pair(secret))
    for _ in range(parts_count-2):
        change = res.pop(randint(0, len(res)-1))
        res.extend(get_rand_pair(change))

    return res
