from collections.abc import AsyncIterator, Iterable
from typing import Protocol

from core.domain.task_group import TaskGroup, TaskGroupFields, TaskGroupIdentifier, TaskGroupQuery
from core.domain.task_group_update import TaskGroupUpdate
from core.domain.users import UserIdentifier
from core.domain.version_major import VersionMajor


class TaskGroupStorage(Protocol):
    # TODO[versionv1]: this method is deprecated, use get_task_group_by_id instead
    async def get_task_group_by_iteration(self, task_id: str, task_schema_id: int, iteration: int) -> TaskGroup: ...

    async def get_task_group_by_id(
        self,
        task_id: str,
        id: TaskGroupIdentifier,
        include: Iterable[TaskGroupFields] | None = None,
    ) -> TaskGroup: ...

    async def increment_run_count(self, task_id: str, task_schema_id: int, iteration: int, increment: int): ...

    # TODO[versionv1]: this method is deprecated, use update_task_group_by_id instead
    async def update_task_group(
        self,
        task_id: str,
        task_schema_id: int,
        iteration: int,
        update: TaskGroupUpdate,
        user: UserIdentifier | None = None,
    ) -> TaskGroup: ...

    async def update_task_group_by_id(
        self,
        task_id: str,
        id: TaskGroupIdentifier,
        update: TaskGroupUpdate,
        user: UserIdentifier | None = None,
    ) -> TaskGroup: ...

    async def add_benchmark_for_dataset(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        iterations: set[int],
    ): ...

    async def remove_benchmark_for_dataset(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        iterations: set[int],
    ): ...

    def list_task_groups(
        self,
        query: TaskGroupQuery,
        include: Iterable[TaskGroupFields] | None = None,
    ) -> AsyncIterator[TaskGroup]: ...

    async def first_id_for_schema(self, task_id: str, schema_id: int) -> str | None: ...

    async def get_latest_group_iteration(self, task_id: str, task_schema_id: int) -> TaskGroup | None: ...

    async def get_previous_major(self, task_id: str, task_schema_id: int, major: int) -> TaskGroup | None: ...

    async def save_task_group(self, task_id: str, hash: str) -> tuple[TaskGroup, bool]: ...

    def list_version_majors(self, task_id: str, task_schema_id: int | None) -> AsyncIterator[VersionMajor]: ...

    async def map_iterations(self, task_id: str, task_schema_id: int, iterations: set[int]) -> dict[int, str]: ...
