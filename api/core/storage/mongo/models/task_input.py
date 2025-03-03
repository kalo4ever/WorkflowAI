from typing import Any, Self

from core.domain.task_input import TaskInput, TaskInputQuery
from core.domain.task_variant import SerializableTaskVariant
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.task_metadata import TaskMetadataSchema
from core.storage.mongo.utils import projection


class TaskInputDocument(BaseDocumentWithID):
    task: TaskMetadataSchema | None = None

    # Can be none when projected out
    task_input: dict[str, Any] | None = None
    task_input_hash: str = ""
    task_input_preview: str = ""

    datasets: list[str] | None = None

    example_id: str | None = None
    example_preview: str | None = None

    @classmethod
    def from_domain(
        cls,
        task: SerializableTaskVariant,
        task_input: TaskInput,
        tenant: str = "",
    ) -> Self:
        if task_input.task_input is None:
            raise ValueError("Task input must be provided")
        return cls(
            tenant=tenant,
            task=TaskMetadataSchema.from_resource(task),
            task_input=task_input.task_input,
            task_input_hash=task_input.task_input_hash,
            task_input_preview=task_input.task_input_preview,
            datasets=list(task_input.datasets) if task_input.datasets else None,
            example_id=task_input.example_id,
            example_preview=task_input.example_preview,
        )

    def to_domain(self):
        return TaskInput(
            task_input=self.task_input,
            task_input_hash=self.task_input_hash,
            task_input_preview=self.task_input_preview,
            datasets=set(self.datasets) if self.datasets else None,
            example_id=self.example_id,
            example_preview=self.example_preview,
        )

    @classmethod
    def build_filter(cls, tenant: str, query: TaskInputQuery) -> dict[str, Any]:
        filter = {
            "tenant": tenant,
            "task.id": query.task_id,
            "task.schema_id": query.task_schema_id,
        }
        if query.dataset_id:
            filter["datasets"] = query.dataset_id
        if query.example_id:
            filter["example_id"] = query.example_id
        return filter

    @classmethod
    def build_project(cls, query: TaskInputQuery) -> dict[str, Any] | None:
        return projection(include=query.include_fields, exclude=query.exclude_fields)
