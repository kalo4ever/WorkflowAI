from api.broker import broker
from api.jobs.common import ReviewsServiceDep
from core.domain.events import AIReviewCompletedEvent


@broker.task()
async def assign_review_to_runs(event: AIReviewCompletedEvent, review_service: ReviewsServiceDep):
    await review_service.assign_review_to_runs(
        task_id=event.task_id,
        task_schema_id=event.task_schema_id,
        task_input_hash=event.task_input_hash,
        task_output_hash=event.task_output_hash,
        reviewer_type="ai",
        review_id=event.review_id,
    )


JOBS = [assign_review_to_runs]
