from api.jobs.common import ReviewsServiceDep
from core.domain.events import RecomputeReviewBenchmarkEvent

from ..broker import broker


@broker.task(retry_on_error=True)
async def recompute_review_benchmark(event: RecomputeReviewBenchmarkEvent, reviews_service: ReviewsServiceDep):
    await reviews_service.recompute_review_benchmark(
        event.task_id,
        event.task_schema_id,
        run_id=event.run_id,
        iterations=event.iterations,
        input_hashes=event.input_hashes,
        cached_run_id=event.cached_run_id,
    )


JOBS = [recompute_review_benchmark]
