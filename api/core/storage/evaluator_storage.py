from typing import AsyncGenerator, Optional, Protocol

from core.domain.task_evaluator import EvaluatorType, EvaluatorTypeName, TaskEvaluator


class EvaluatorStorage(Protocol):
    async def add_task_evaluator(
        self,
        task_id: str,
        task_schema_id: int,
        task_evaluator: TaskEvaluator,
    ) -> TaskEvaluator: ...

    def list_task_evaluators(
        self,
        task_id: str,
        task_schema_id: int,
        types: Optional[set[EvaluatorTypeName]] = None,
        active: bool | None = True,
        limit: int | None = None,
    ) -> AsyncGenerator[TaskEvaluator, None]: ...

    async def get_task_evaluator(self, task_id: str, task_schema_id: int, evaluator_id: str) -> TaskEvaluator: ...

    async def set_task_evaluator_active(
        self,
        task_id: str,
        task_schema_id: int,
        evaluator_id: str,
        active: bool,
    ) -> None: ...

    async def patch_evaluator(
        self,
        id: str,
        active: bool,
        is_loading: bool,
        evaluator_type: EvaluatorType,
    ) -> None: ...

    async def deactivate_evaluators(
        self,
        task_id: str,
        task_schema_id: int,
        except_id: str | None,
        types: set[EvaluatorTypeName] | None,
    ) -> None: ...
