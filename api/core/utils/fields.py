from datetime import datetime, timezone

from core.utils.uuid import uuid7


def datetime_factory() -> datetime:
    return datetime.now(timezone.utc)


def id_factory() -> str:
    return str(uuid7())


def uuid_zero():
    return uuid7(lambda: 0, lambda: 0)


def datetime_zero() -> datetime:
    return datetime(1970, 1, 1)


def date_zero():
    return datetime(1970, 1, 1).date()
