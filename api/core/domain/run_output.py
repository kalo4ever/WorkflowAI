from collections.abc import Sequence
from typing import NamedTuple

from core.domain.fields.internal_reasoning_steps import InternalReasoningStep
from core.domain.task_run import Run
from core.domain.tool_call import ToolCall, ToolCallRequestWithID
from core.domain.types import TaskOutputDict


class RunOutput(NamedTuple):
    task_output: TaskOutputDict
    tool_calls: Sequence[ToolCall] | None = None
    tool_call_requests: Sequence[ToolCallRequestWithID] | None = None
    reasoning_steps: list[InternalReasoningStep] | None = None

    @classmethod
    def from_run(cls, run: Run):
        return cls(
            task_output=run.task_output,
            tool_calls=run.tool_calls,
            tool_call_requests=run.tool_call_requests,
            reasoning_steps=run.reasoning_steps,
        )
