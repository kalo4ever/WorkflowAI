from typing import Any, Optional, Protocol

from core.domain.analytics_events.analytics_events import RunTrigger
from core.domain.deprecated.task import Task, TaskInput, TaskOutput
from core.domain.types import CacheUsage
from core.domain.version_reference import VersionReference
from core.runners.abstract_runner import AbstractRunner


class WorkflowAIInterface(Protocol):
    async def run(
        self,
        task: Task[TaskInput, TaskOutput],
        input: TaskInput,
        runner: Optional[AbstractRunner[Any]] = None,
        group: Optional[VersionReference] = None,
        task_run_id: Optional[str] = None,
        cache: CacheUsage = "auto",
        labels: Optional[set[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        trigger: RunTrigger | None = None,
    ) -> TaskOutput: ...
