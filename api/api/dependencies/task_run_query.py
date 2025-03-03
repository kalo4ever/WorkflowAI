from datetime import datetime
from typing import Annotated, Literal, Optional

from fastapi import Depends, Query

from core.domain.task_run_query import (
    SerializableTaskRunField,
    SerializableTaskRunQuery,
    TaskRunQueryUniqueBy,
)

from .page_query import PageQueryDep
from .task_query import TaskQueryDep


def task_run_query_dependency(
    page_query: PageQueryDep,
    task_query: TaskQueryDep,
    task_input_hash: Optional[str] = Query(None, description="The hash of the task input"),
    task_output_hash: Optional[str] = Query(None, description="The hash of the task output"),
    group_id: Optional[str] = Query(default=None, description="An id of a task run group"),
    unique_by: TaskRunQueryUniqueBy = Query(
        default=None,
        description="Make sure only one task run is returned per unique value of the requested field",
    ),
    exclude_fields: Optional[list[SerializableTaskRunField]] = Query(
        default=None,
        description="A list of fields to exclude from the response",
    ),
    include_fields: Optional[list[SerializableTaskRunField]] = Query(
        default=None,
        description="A list of fields to include in the response",
    ),
    created_after: datetime | None = Query(default=None, description="Only return task runs created after this date"),
    status: list[Literal["success", "failure"]] | None = Query(
        default=None,
        description="The status of the task run. By default, only successful runs are returned",
    ),
) -> SerializableTaskRunQuery:
    return SerializableTaskRunQuery(
        task_input_hashes={task_input_hash} if task_input_hash else None,
        task_output_hash=task_output_hash,
        group_ids={group_id} if group_id else None,
        unique_by={unique_by} if unique_by else None,
        exclude_fields=set(exclude_fields) if exclude_fields else None,
        include_fields=set(include_fields) if include_fields else None,
        created_after=created_after,
        status={"success"} if not status else set(status),
        **page_query.model_dump(),
        **task_query.model_dump(),
    )


TaskRunQueryDep = Annotated[SerializableTaskRunQuery, Depends(task_run_query_dependency)]
