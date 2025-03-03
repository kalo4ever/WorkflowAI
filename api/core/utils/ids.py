import secrets


def id_uint32() -> int:
    return secrets.randbelow(2**32)
