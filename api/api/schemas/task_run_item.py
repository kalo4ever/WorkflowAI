from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from api.schemas.version_properties import ShortVersionProperties
from core.domain.error_response import ErrorCode, ErrorResponse
from core.domain.task_group import TaskGroup
from core.domain.task_run import SerializableTaskRunBase


class TaskRunItem(BaseModel):
    """A lightweight version of a task run that is returned in list contexts"""

    id: str = Field(description="the id of the task run")
    task_id: str = Field(description="the id of the task")
    task_schema_id: int = Field(description="The id of the task run's schema")
    task_input_preview: str = Field(description="A preview of the input data")
    task_output_preview: str = Field(description="A preview of the output data")

    class TaskGroup(BaseModel):
        iteration: int = Field(description="The iteration of the group")
        properties: ShortVersionProperties = Field(description="The properties of the group")

        @classmethod
        def from_domain(cls, group: TaskGroup):
            return cls(
                iteration=group.iteration,
                properties=ShortVersionProperties.from_domain(group.properties),
            )

    group: TaskGroup

    status: Literal["success", "failure"]

    class Error(BaseModel):
        code: ErrorCode | str

        @classmethod
        def from_domain(cls, error: ErrorResponse.Error):
            return cls(
                code=error.code,
            )

    error: Error | None

    duration_seconds: float | None
    cost_usd: float | None
    created_at: datetime = Field(description="The time the task run was created")
    updated_at: datetime = Field(description="The time the task run was last updated")

    example_id: str | None = Field(description="The id of the example that share the same input as the task run")

    user_review: Literal["positive", "negative"] | None
    ai_review: Literal["positive", "negative", "unsure", "in_progress"] | None
    author_uid: int | None

    @classmethod
    def from_domain(cls, run: SerializableTaskRunBase):
        return cls(
            id=run.id,
            task_id=run.task_id,
            task_input_preview=run.task_input_preview,
            task_output_preview=run.task_output_preview,
            task_schema_id=run.task_schema_id,
            group=cls.TaskGroup.from_domain(run.group),
            status=run.status,
            error=cls.Error.from_domain(run.error) if run.error else None,
            duration_seconds=run.duration_seconds,
            cost_usd=run.cost_usd,
            created_at=run.created_at,
            updated_at=run.updated_at,
            example_id=run.example_id,
            user_review=run.user_review,
            ai_review=run.ai_review,
            author_uid=run.author_uid,
        )
