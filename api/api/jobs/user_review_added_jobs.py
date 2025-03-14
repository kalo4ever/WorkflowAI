from api.jobs.common import ReviewsServiceDep
from core.domain.events import UserReviewAddedEvent

from ..broker import broker


@broker.task()
async def update_ai_reviewer_from_user_review(event: UserReviewAddedEvent, review_service: ReviewsServiceDep):
    await review_service.update_ai_reviewer_from_user_review(
        event.task_id,
        event.task_schema_id,
        event.task_input_hash,
        event.task_output_hash,
        event.review_id,
        event.comment,
        event.in_response_to,
    )


@broker.task()
async def assign_review_to_runs(event: UserReviewAddedEvent, review_service: ReviewsServiceDep):
    await review_service.assign_review_to_runs(
        event.task_id,
        event.task_schema_id,
        task_input_hash=event.task_input_hash,
        task_output_hash=event.task_output_hash,
        reviewer_type="user",
        review_id=event.review_id,
    )


@broker.task()
async def trigger_runs_for_benchmark(event: UserReviewAddedEvent, review_service: ReviewsServiceDep):
    await review_service.trigger_runs_for_benchmark(
        event.task_id,
        event.task_schema_id,
        task_input_hash=event.task_input_hash,
        is_first_review=event.is_first_review,
        run_id=event.run_id,
    )


JOBS = [update_ai_reviewer_from_user_review, assign_review_to_runs, trigger_runs_for_benchmark]
