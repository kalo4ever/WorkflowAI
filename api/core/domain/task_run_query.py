import datetime
from typing import Literal, Optional

from pydantic import Field

from core.domain.search_query import FieldQuery, SpecialFieldQueryName

from .page_query_mixin import PageQueryMixin
from .task_query_mixin import TaskQueryMixin

TaskRunQueryUniqueBy = Literal["task_input_hash", "task_output_hash", "version_id"]

SerializableTaskRunField = Literal[
    "task_input",
    "task_input_hash",
    "_id",
    "task_output",
    "task_output_hash",
    "task_schema_id",
    "llm_completions",
    "version_id",
    "group.iteration",
    "group.properties",  # TODO: remove
    "created_at",
    "status",
    "metadata",
    "tool_calls",
    "tool_call_requests",
    "eval_hash",
]


class SerializableTaskRunQuery(TaskQueryMixin, PageQueryMixin):
    """Filter for task runs"""

    task_input_hashes: set[str] | None = Field(default=None, description="The hash of the task input")
    task_output_hash: Optional[str] = Field(default=None, description="The hash of the task output")

    # Group metadata
    group_ids: Optional[set[str]] = Field(default=None, description="A list of task run group ids")

    unique_by: set[TaskRunQueryUniqueBy] | None = Field(
        default=None,
        description="Make sure only one task run is returned per unique value of the requested field",
    )

    include_fields: set[SerializableTaskRunField] | None = Field(
        default=None,
        description="A list of fields to include in the response",
    )

    exclude_fields: Optional[set[SerializableTaskRunField]] = Field(
        default=None,
        description="A list of fields to exclude from the response",
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="True if the task run is triggered using sdk/api, False for other sources, None default",
    )

    created_after: datetime.datetime | None = None

    created_before: datetime.datetime | None = None

    status: set[Literal["success", "failure"]] | None = None

    metadata: Optional[dict[str, str]] = None

    def _assign_value_from_special_fields(self, field: FieldQuery):
        try:
            special_field_name = SpecialFieldQueryName(field.field_name)
        except ValueError:
            return False

        match special_field_name:
            case SpecialFieldQueryName.REVIEW:
                return False
