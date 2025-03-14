from typing import Annotated, Literal, Optional

from fastapi import Depends, Query

from api.dependencies.page_query import PageQueryDep
from api.dependencies.task_query import TaskQueryDep
from core.domain.task_example_query import SerializableTaskExampleField, SerializableTaskExampleQuery


# Using a string so that the vector can be passed as a single query pararm
# task_input_vector=1,2,3 instead of task_input_vector=1&vector=2
def _parse_input_vector(vector: Optional[str]) -> Optional[list[float]]:
    if not vector:
        return None
    return [float(v) for v in vector.split(",")]


def task_example_query_dependency(
    page_query: PageQueryDep,
    task_query: TaskQueryDep,
    sort_by: Literal["created_at", "random", "recent"] = Query("recent"),
    is_training: Optional[bool] = Query(
        default=None,
        description="Whether to include or include the training set. Omit to ignore",
    ),
    task_input_vector: Optional[str] = Query(
        default=None,
        description="A vector for semantic search of the input. As a list of floats or a comma separated float string",
        pattern=r"\d+(.\d+)?(,\d+(.\d+)?)*",
    ),
    from_correction: Optional[bool] = Query(
        default=None,
        description="filter whether examples come from corrections. Omit to ignore",
    ),
    unique_by: Literal["task_input_hash", "task_output_hash", None] = Query(
        default=None,
        description="Make sure only one task run is returned per unique value of the requested field",
    ),
    exclude_fields: Optional[list[SerializableTaskExampleField]] = Query(
        default=None,
        description="A list of fields to exclude from the response",
    ),
) -> SerializableTaskExampleQuery:
    return SerializableTaskExampleQuery(
        sort_by=SerializableTaskExampleQuery.SortBy(sort_by),
        is_training=is_training,
        task_input_vector=_parse_input_vector(task_input_vector),
        from_correction=from_correction,
        unique_by=unique_by,
        exclude_fields=set(exclude_fields) if exclude_fields else None,
        **page_query.model_dump(),
        **task_query.model_dump(),
    )


TaskExampleQueryDep = Annotated[SerializableTaskExampleQuery, Depends(task_example_query_dependency)]
