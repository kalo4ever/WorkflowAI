from typing import Protocol

from core.domain.task_info import TaskInfo
from core.storage.models import TaskUpdate


class TaskStorage(Protocol):
    async def is_task_public(self, task_id: str) -> bool: ...

    async def get_task_info(self, task_id: str) -> TaskInfo: ...

    async def update_task(self, task_id: str, update: TaskUpdate) -> TaskInfo: ...
