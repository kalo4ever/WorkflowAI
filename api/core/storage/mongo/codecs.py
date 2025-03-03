import datetime
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

from bson.codec_options import TypeEncoder, TypeRegistry
from pydantic_core import Url


class DateEncoder(TypeEncoder):
    python_type = datetime.date  # type: ignore
    bson_type = datetime.datetime  # type: ignore

    def transform_python(self, value: datetime.date) -> datetime.datetime:
        """Function that transforms a custom type value into a type that BSON can encode."""
        # Convert the date object to a datetime object at midnight
        return datetime.datetime(value.year, value.month, value.day, tzinfo=datetime.timezone.utc)


class TimeEncoder(TypeEncoder):
    python_type = datetime.time  # type: ignore
    bson_type = str  # type: ignore

    def transform_python(self, value: datetime.time) -> str:
        """Function that transforms a custom type value into a type that BSON can encode."""
        # Convert the date object to a datetime object at midnight
        return value.isoformat()


class ZoneInfoEncoder(TypeEncoder):
    python_type = ZoneInfo  # type: ignore
    bson_type = str  # type: ignore

    def transform_python(self, value: ZoneInfo) -> str:
        """Function that transforms a custom type value into a type that BSON can encode."""
        # Convert the date object to a datetime object at midnight
        return value.key


class UrlEncoder(TypeEncoder):
    python_type = Url  # type: ignore
    bson_type = str  # type: ignore

    def transform_python(self, value: Url) -> str:
        """Function that transforms a custom type value into a type that BSON can encode."""
        # Convert the date object to a datetime object at midnight
        return str(value)


def fallback_encoder(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Unsupported type {type(value)}")


type_registry = TypeRegistry(
    [
        DateEncoder(),
        TimeEncoder(),
        ZoneInfoEncoder(),
        UrlEncoder(),
    ],
    fallback_encoder=fallback_encoder,
)
