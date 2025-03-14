from datetime import datetime
from typing import Any, Optional, Self

from bson import ObjectId
from bson.errors import InvalidId
from pydantic_core import core_schema


class PyObjectID(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.no_info_plain_validator_function(cls.cast),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ],
                    ),
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: ObjectId(x)),
        )

    @classmethod
    def new(cls) -> Self:
        return cls(ObjectId())

    @classmethod
    def cast(cls, value: Any) -> Self:
        oid = cls.validate(value)
        return cls(oid)

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except InvalidId:
            raise AssertionError("Invalid ObjectId")

    @classmethod
    def from_str(cls, val: str | None) -> Optional[Self]:
        return cls(val) if val else None

    @classmethod
    def to_str(cls, val: Optional[Self]) -> str:
        return str(val) if val else ""

    @property
    def generation_time(self) -> datetime:
        return ObjectId(self).generation_time
