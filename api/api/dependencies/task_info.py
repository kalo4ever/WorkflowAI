import logging
from typing import Annotated

from fastapi import Depends, HTTPException

from api.dependencies.path_params import TaskID
from api.dependencies.storage import StorageDep
from core.domain.task_info import TaskInfo
from core.storage import TaskTuple

logger = logging.getLogger(__name__)


async def task_info_dependency(
    task_id: TaskID,
    storage: StorageDep,
) -> TaskInfo | None:
    """Dependency that checks if a task is banned and raises 403 if it is"""
    try:
        return await storage.tasks.get_task_info(task_id)
    except Exception as e:
        # TODO: we should remove the exception here
        logger.error(
            "Error getting task info",
            extra={
                "task_id": task_id,
                "error": e,
            },
        )
        return None


TaskInfoDep = Annotated[TaskInfo | None, Depends(task_info_dependency)]


async def task_tuple_dependency(
    task_info: TaskInfoDep,
) -> TaskTuple:
    if task_info is None:
        raise HTTPException(status_code=404, detail="Task info not found")
    return task_info.id_tuple


TaskTupleDep = Annotated[TaskTuple, Depends(task_tuple_dependency)]
