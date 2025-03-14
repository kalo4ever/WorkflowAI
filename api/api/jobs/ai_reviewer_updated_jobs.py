from api.jobs.common import ReviewsServiceDep
from core.domain.events import AIReviewerUpdatedEvent

from ..broker import broker


@broker.task()
async def trigger_reviews_for_ai_reviewer_updates(event: AIReviewerUpdatedEvent, review_service: ReviewsServiceDep):
    await review_service.trigger_reviews_for_ai_reviewer_updates(
        task_id=event.task_id,
        task_schema_id=event.task_schema_id,
        task_input_hash=event.task_input_hash,
        evaluator_id=event.evaluator_id,
        input_evaluation_id=event.input_evaluation_id,
        evaluator_did_change=event.evaluator_did_change,
    )


JOBS = [trigger_reviews_for_ai_reviewer_updates]
