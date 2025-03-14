from typing import Any

from core.domain.task_query_mixin import TaskQueryMixin


def build_task_query_filter(tenant: str, query: TaskQueryMixin) -> dict[str, Any]:
    filter: dict[str, Any] = {
        "tenant": tenant,
    }

    if query.task_id:
        filter["task.id"] = query.task_id

    if query.task_schema_id:
        filter["task.schema_id"] = query.task_schema_id

    if query.task_input_schema_version:
        filter["task.input_class_version"] = query.task_input_schema_version
    if query.task_output_schema_version:
        filter["task.output_class_version"] = query.task_output_schema_version

    return filter
