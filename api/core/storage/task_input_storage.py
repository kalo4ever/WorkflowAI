from collections.abc import AsyncIterator, Iterable
from typing import Protocol

from core.domain.task_input import TaskInput, TaskInputFields, TaskInputQuery
from core.domain.task_variant import SerializableTaskVariant


class TaskInputsStorage(Protocol):
    async def create_inputs(self, task: SerializableTaskVariant, task_inputs: Iterable[TaskInput]): ...

    async def create_input(self, task: SerializableTaskVariant, task_input: TaskInput) -> TaskInput: ...

    async def attach_example(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
        example_id: str,
        example_preview: str,
    ) -> None: ...

    async def detach_example(self, task_id: str, task_schema_id: int, input_hash: str, example_id: str) -> None: ...

    async def remove_inputs_from_datasets(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        input_hashes: list[str],
    ): ...

    def list_inputs(self, query: TaskInputQuery) -> AsyncIterator[TaskInput]: ...

    async def get_input_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
        exclude: Iterable[TaskInputFields] | None = None,
    ) -> TaskInput: ...

    async def count_inputs(self, query: TaskInputQuery) -> tuple[int, int]: ...
