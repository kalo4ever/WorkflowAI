from api.jobs.common import ReviewsServiceDep
from core.domain.events import AIReviewerBuildStartedEvent

from ..broker import broker


@broker.task()
async def update_benchmark(
    event: AIReviewerBuildStartedEvent,
    review_service: ReviewsServiceDep,
):
    await review_service.mark_benchmark_as_building_evaluator(
        task_id=event.task_id,
        task_schema_id=event.task_schema_id,
        is_building=True,
    )


JOBS = [update_benchmark]
