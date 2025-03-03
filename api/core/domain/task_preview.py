from typing import Any

from pydantic import BaseModel, Field


class TaskPreview(BaseModel):
    input: dict[str, Any] = Field(
        description="The preview input for the task",
    )

    output: dict[str, Any] = Field(
        description="The preview output for the task",
    )
