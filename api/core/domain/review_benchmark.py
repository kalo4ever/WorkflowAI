from pydantic import BaseModel

from core.domain.task_group_properties import TaskGroupProperties


class ReviewBenchmark(BaseModel):
    task_id: str
    task_schema_id: int

    class VersionAggregation(BaseModel):
        iteration: int
        properties: TaskGroupProperties

        positive_review_count: int
        positive_user_review_count: int
        negative_review_count: int
        negative_user_review_count: int
        unsure_review_count: int
        in_progress_review_count: int

        total_run_count: int
        run_failed_count: int
        run_in_progress_count: int

        average_cost_usd: float | None
        average_duration_seconds: float | None

    is_loading_new_ai_reviewer: bool

    results: list[VersionAggregation]
