from typing import Self

from pydantic import BaseModel

from core.domain.task_variant import SerializableTaskVariant


class TaskMetadataSchema(BaseModel):
    id: str = ""
    schema_id: int = 0
    input_class_version: str = ""
    output_class_version: str = ""

    @classmethod
    def from_resource(cls, task: SerializableTaskVariant) -> Self:
        return cls(
            id=task.task_id,
            input_class_version=task.input_schema.version,
            output_class_version=task.output_schema.version,
            schema_id=task.task_schema_id,
        )
