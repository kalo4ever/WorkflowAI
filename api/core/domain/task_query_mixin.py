from typing import Optional

from pydantic import BaseModel, Field


class TaskQueryMixin(BaseModel):
    task_id: str | None = Field(..., description="The id of the task")
    task_schema_id: int | None = Field(default=None, description="The schema id")
    task_input_schema_version: Optional[str] = Field(default=None, description="The version of the task input class")
    task_output_schema_version: Optional[str] = Field(default=None, description="The version of the task output class")
