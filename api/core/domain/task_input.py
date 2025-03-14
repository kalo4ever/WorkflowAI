from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

from core.domain.page_query_mixin import PageQueryMixin

CommonTaskInputFields = Literal["task_input", "task_input_hash"]

TaskInputFields = CommonTaskInputFields | Literal["example_id", "datasets"]


class TaskInputQuery(PageQueryMixin):
    task_id: str
    task_schema_id: int

    dataset_id: str | None = None

    exclude_fields: set[TaskInputFields] | None = Field(
        default=None,
        description="A set of fields to exclude from the task input. If None, no fields will be excluded",
    )

    include_fields: set[TaskInputFields] | None = None

    example_id: str | None = None


class TaskInput(BaseModel):
    task_input_preview: str = ""
    task_input: dict[str, Any] | None = Field(default=None, description="The input or None if the field was excluded")
    task_input_hash: str = Field(description="a hash describing the input")

    datasets: set[str] | None = None

    example_id: str | None = Field(default=None, description="The id of the associated example")
    example_preview: str | None = Field(default=None, description="The preview of the associated example")


class TaskInputReference(BaseModel):
    task_input: dict[str, Any] | None = Field(
        default=None,
        description="A task input. Only one of task_input or task_input_hash should be provided",
    )
    task_input_hash: str | None = Field(
        default=None,
        description="a hash describing an input that already exists in out database. Only one of task_input or task_input_hash should be provided",
    )

    @model_validator(mode="after")
    def post_validate(self) -> Self:
        if self.task_input is None and self.task_input_hash is None:
            raise ValueError("Either task_input or task_input_hash must be provided")
        if self.task_input and self.task_input_hash:
            raise ValueError("Only one of task_input or task_input_hash should be provided")
        return self
