from typing import Any, Self

from pydantic import BaseModel

from core.domain.task_io import SerializableTaskIO


class TaskIOSchema(BaseModel):
    """Schema for task input and output"""

    version: str
    json_schema: dict[str, Any]

    @classmethod
    def from_resource(cls, task_io: SerializableTaskIO) -> Self:
        return cls(
            version=task_io.version,
            json_schema=task_io.json_schema,
        )

    def to_resource(self) -> SerializableTaskIO:
        return SerializableTaskIO(
            version=self.version,
            json_schema=self.json_schema,
        )
