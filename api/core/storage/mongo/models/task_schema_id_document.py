from pydantic import Field

from .base_document import BaseDocument


class TaskSchemaIdDocument(BaseDocument):
    """
    A document identifying schemas for a given task id. The schema of a task represents
    the types of the task input and ouput.
    """

    # TODO[uid]: remove, all task schema ids should have a uid
    slug: str = Field(..., description="The task slug")

    task_uid: int = Field(default=0, description="The task uid")

    latest_idx: int = Field(..., description="The latest index of the task schemas")

    idx_mapping: dict[str, int] = Field(..., description="A mapping of schema hashes to their int ids.")
