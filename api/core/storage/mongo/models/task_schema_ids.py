from pydantic import Field

from .base_document import BaseDocument


class TaskSchemaIndexSchema(BaseDocument):
    """
    A document identifying schemas for a given task id. The schema of a task represents
    the types of the task input and ouput.
    """

    slug: str = Field(..., description="The task slug")

    latest_idx: int = Field(..., description="The latest index of the task schemas")

    idx_mapping: dict[str, int] = Field(..., description="A mapping of schema hashes to their int ids.")
