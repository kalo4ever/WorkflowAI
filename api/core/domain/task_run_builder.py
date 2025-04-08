from datetime import UTC, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from core.domain.consts import METADATA_KEY_INFERENCE_SECONDS
from core.domain.error_response import ErrorResponse
from core.domain.llm_completion import LLMCompletion
from core.domain.run_output import RunOutput
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_run import Run
from core.domain.task_run_reply import RunReply
from core.domain.task_variant import SerializableTaskVariant
from core.domain.types import TaskInputDict
from core.utils.uuid import uuid7


class TaskRunBuilder(BaseModel):
    """
    A task run is an instance of a task with a specific input and output.

    This object is used to build a task run that will later be recorded.
    """

    id: str = Field(default_factory=lambda: str(uuid7()))

    task: SerializableTaskVariant

    # The input that was used to execute the task
    task_input: TaskInputDict

    task_input_hash: str = ""

    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))

    example_id: Optional[str] = None

    properties: TaskGroupProperties = Field(..., description="The properties used for executing the run.")

    tags: list[str] = Field(default_factory=list, description="A list of tags to associate with the run group.")

    # The built task run
    _task_run: Run | None = None

    labels: Optional[set[str]] = None

    metadata: dict[str, Any] | None = Field(default=None)

    llm_completions: list[LLMCompletion] = Field(default_factory=list)

    # The id of the tenant that created the task run
    # if different from the task's tenant
    author_tenant: str | None = None  # TODO: remove in favor of author uid
    author_uid: int | None = None

    private_fields: set[str] | None = None

    version_changed: bool | None = None

    # Whether the builder concerns a reply to a previous run
    reply: RunReply | None = None

    def add_metadata(self, key: str, value: Any) -> None:
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Any | None:
        if not self.metadata:
            return None
        return self.metadata.get(key)

    def add_label(self, label: str) -> None:
        if self.labels is None:
            self.labels = set()
        self.labels.add(label)

    @model_validator(mode="after")
    def set_task_input_hash(self):
        if not self.task_input_hash:
            self.task_input_hash = self.task.compute_input_hash(self.task_input)
        return self

    @property
    def task_run(self) -> Run | None:
        return self._task_run

    def build(
        self,
        output: RunOutput | None,
        from_cache: bool = False,
        end_time: Optional[datetime] = None,
        error: Optional[ErrorResponse.Error] = None,
    ) -> Run:
        """
        Builds the task run object
        """
        if self._task_run:
            if output and self._task_run.task_output != output.task_output:
                raise ValueError("Task output has already been set")
            return self._task_run

        end_time = end_time or datetime.now(UTC)

        _cost_usd = None
        if self.llm_completions:
            _cost_usd = sum(c.usage.cost_usd for c in self.llm_completions if c.usage and c.usage.cost_usd is not None)

        metadata = self.metadata or {}
        if self.llm_completions:
            seconds = sum(c.duration_seconds for c in self.llm_completions if c.duration_seconds is not None)
            if seconds:
                metadata[METADATA_KEY_INFERENCE_SECONDS] = seconds

        self._task_run = Run(
            id=self.id,
            version_changed=self.version_changed,
            start_time=self.start_time,
            end_time=end_time,
            duration_seconds=(end_time - self.start_time).total_seconds() if not error else None,
            cost_usd=_cost_usd,
            task_id=self.task.task_id,
            task_schema_id=self.task.task_schema_id,
            task_input=self.task_input,
            task_input_hash=self.task_input_hash,
            task_output=output.task_output if output else {},
            task_output_hash=self.task.compute_output_hash(output.task_output) if output else "",
            group=TaskGroup(
                id=self.properties.model_hash(),
                properties=self.properties,
                tags=self.tags,
            ),
            from_cache=from_cache,
            labels=self.labels,
            llm_completions=self.llm_completions,
            tool_calls=list(output.tool_calls) if output and output.tool_calls else None,
            tool_call_requests=list(output.tool_call_requests) if output and output.tool_call_requests else None,
            reasoning_steps=output.reasoning_steps if output else None,
            example_id=self.example_id,
            metadata=metadata or None,
            status="failure" if error else "success",
            error=error,
            author_tenant=self.author_tenant,
            author_uid=self.author_uid,
            private_fields=self.private_fields,
        )
        return self._task_run
