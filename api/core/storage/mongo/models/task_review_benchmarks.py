from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.domain.review_benchmark import ReviewBenchmark
from core.domain.task_group_properties import TaskGroupProperties
from core.storage.mongo.models.base_document import BaseDocumentWithID, TaskIdAndSchemaMixin


class TaskReviewBenchmarkDocument(BaseDocumentWithID, TaskIdAndSchemaMixin):
    class VersionAggregation(BaseModel):
        iteration: int
        properties: dict[str, Any]

        positive_review_count: int | None = None
        positive_user_review_count: int | None = None
        negative_review_count: int | None = None
        negative_user_review_count: int | None = None
        unsure_review_count: int | None = None
        in_progress_review_count: int | None = None

        total_run_count: int | None = None
        run_failed_count: int | None = None
        run_in_progress_ids: list[str] | None = None

        average_cost_usd: float | None = None
        average_duration_seconds: float | None = None

        updated_at: datetime | None = None

        def to_domain(self) -> ReviewBenchmark.VersionAggregation:
            return ReviewBenchmark.VersionAggregation(
                iteration=self.iteration,
                properties=TaskGroupProperties.model_validate(self.properties),
                positive_review_count=self.positive_review_count or 0,
                negative_review_count=self.negative_review_count or 0,
                unsure_review_count=self.unsure_review_count or 0,
                in_progress_review_count=self.in_progress_review_count or 0,
                total_run_count=self.total_run_count or 0,
                run_failed_count=self.run_failed_count or 0,
                run_in_progress_count=len(self.run_in_progress_ids) if self.run_in_progress_ids else 0,
                average_cost_usd=self.average_cost_usd or None,
                average_duration_seconds=self.average_duration_seconds or None,
                positive_user_review_count=self.positive_user_review_count or 0,
                negative_user_review_count=self.negative_user_review_count or 0,
            )

    is_loading_new_ai_reviewer: bool = False

    results: list[VersionAggregation] = Field(default_factory=list)

    def to_domain(self) -> ReviewBenchmark:
        return ReviewBenchmark(
            task_id=self.task_id,
            task_schema_id=self.task_schema_id,
            is_loading_new_ai_reviewer=self.is_loading_new_ai_reviewer,
            results=[VersionAggregation.to_domain() for VersionAggregation in self.results],
        )
