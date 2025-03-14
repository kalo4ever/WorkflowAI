from typing import AsyncIterator, Protocol

from core.domain.input_evaluation import InputEvaluation


class InputEvaluationStorage(Protocol):
    async def get_latest_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
    ) -> InputEvaluation | None: ...

    async def create_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_evaluation: InputEvaluation,
    ) -> InputEvaluation: ...

    async def get_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_evaluation_id: str,
    ) -> InputEvaluation: ...

    def list_input_evaluations_unique_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
    ) -> AsyncIterator[InputEvaluation]: ...

    async def unique_input_hashes(self, task_id: str, task_schema_id: int) -> set[str]: ...
