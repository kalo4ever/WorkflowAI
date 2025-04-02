from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from api.routers.common import DeprecatedVersionReference
from core.domain.task_group import TaskGroup
from core.domain.task_run import SerializableTaskRun
from core.domain.task_variant import SerializableTaskVariant
from core.utils.fields import datetime_factory
from core.utils.uuid import uuid7


class CreateTaskRunRequest(BaseModel):
    task_input: dict[str, Any] = Field(..., description="the input of the task. Must match the input schema")
    task_output: dict[str, Any] = Field(..., description="the output of the task. Must match the output schema")

    group: DeprecatedVersionReference = Field(
        ...,
        description="A reference to the task group the task run belongs to. By default, we consider that the group is external",
    )

    start_time: datetime = Field(default_factory=datetime_factory, description="the time the run was started.")
    end_time: Optional[datetime] = Field(default=None, description="the time the run ended.")

    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata to store with the task run.")

    cost_usd: Optional[float] = Field(default=None, description="The cost of the task run in USD")

    def duration_seconds(self) -> Optional[float]:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def build(self, task_variant: SerializableTaskVariant, task_group: TaskGroup) -> SerializableTaskRun:
        task_variant.enforce(self.task_input, self.task_output)
        return SerializableTaskRun(
            id=str(uuid7(ms=lambda: int(self.start_time.timestamp() * 1000))),
            task_id=task_variant.task_id,
            task_schema_id=task_variant.task_schema_id,
            task_input=self.task_input,
            task_input_hash=task_variant.compute_input_hash(self.task_input),
            task_output=self.task_output,
            task_output_hash=task_variant.compute_output_hash(self.task_output),
            start_time=self.start_time,
            end_time=self.end_time,
            duration_seconds=self.duration_seconds(),
            cost_usd=self.cost_usd,
            group=task_group,
            metadata=self.metadata,
        )
