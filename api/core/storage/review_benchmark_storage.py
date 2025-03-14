from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, TypedDict

from core.domain.review_benchmark import ReviewBenchmark
from core.domain.task_group_properties import TaskGroupProperties


class RunReviewAggregateWithIteration(TypedDict):
    iteration: int  # the iteration

    in_progress_review_count: int | None
    positive_review_count: int | None
    positive_user_review_count: int | None
    negative_review_count: int | None
    negative_user_review_count: int | None
    unsure_review_count: int | None
    average_cost_usd: float | None
    average_duration_seconds: float | None
    total_run_count: int
    failed_run_count: int | None


class ReviewBenchmarkStorage(Protocol):
    async def get_benchmark_versions(
        self,
        task_id: str,
        task_schema_id: int,
    ) -> set[int]: ...

    async def get_review_benchmark(self, task_id: str, task_schema_id: int) -> ReviewBenchmark: ...

    async def add_versions(
        self,
        task_id: str,
        task_schema_id: int,
        versions: list[tuple[int, TaskGroupProperties]],
    ) -> ReviewBenchmark: ...

    async def remove_versions(self, task_id: str, task_schema_id: int, iterations: list[int]) -> ReviewBenchmark: ...

    async def mark_as_loading_new_ai_reviewer(
        self,
        task_id: str,
        task_schema_id: int,
        is_loading_new_ai_reviewer: bool,
    ): ...

    async def add_in_progress_run(self, task_id: str, task_schema_id: int, iteration: int, run_id: str): ...

    async def complete_run(self, task_id: str, task_schema_id: int, iteration: int, run_id: str): ...

    async def update_benchmark(
        self,
        task_id: str,
        task_schema_id: int,
        aggregates: Iterable[RunReviewAggregateWithIteration],
        now: datetime,
    ): ...
