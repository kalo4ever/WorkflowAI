from enum import StrEnum
from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from core.domain.task_input import CommonTaskInputFields
from core.storage.mongo.models.pyobjectid import PyObjectID

from .page_query_mixin import PageQueryMixin
from .task_query_mixin import TaskQueryMixin

SerializableTaskExampleField = (
    CommonTaskInputFields | Literal["_id", "task_output_preview", "task_output", "task_output_hash"]
)


class SerializableTaskExampleQuery(TaskQueryMixin, PageQueryMixin):
    """Filter for examples. Used to query the evaluation database."""

    class SortBy(StrEnum):
        """How to order the returned documents"""

        "Oldest documents are returned first. Use that sorting for fetching the entire data. Safe for pagination."
        CREATED_AT = "created_at"

        "Pick random documents, pagination is not possible"
        RANDOM = "random"

        "Most recent documents are returned first, pagination is possible but newly created objects will not be returned"
        RECENT = "recent"

    sort_by: SortBy = SortBy.RECENT

    is_training: Optional[bool] = Field(
        default=None,
        description="Whether to include or include the training set. Omit to ignore",
    )

    task_input_vector: Optional[list[float]] = Field(
        default=None,
        description="The parsed input vector",
    )

    task_input_hashes: set[str] | None = None

    from_correction: Optional[bool] = Field(
        default=None,
        description="filter whether examples come from corrections. Omit to ignore",
    )

    ids: Optional[set[PyObjectID]] = Field(
        default=None,
        description="The list of example IDs to fetch",
    )

    unique_by: Literal["task_input_hash", "task_output_hash", None] = Field(
        default=None,
        description="Make sure only one task run is returned per unique value of the requested field",
    )

    exclude_fields: Optional[set[SerializableTaskExampleField]] = Field(
        default=None,
        description="A list of fields to exclude from the response",
    )

    include_fields: Optional[set[SerializableTaskExampleField]] = Field(
        default=None,
        description="A list of fields to include in the response",
    )
