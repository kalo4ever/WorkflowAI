from api.broker import broker
from api.jobs.common import ReviewsServiceDep
from core.domain.events import TriggerRunEvaluationEvent


@broker.task(retry_on_error=True)
async def trigger_evaluate_run(event: TriggerRunEvaluationEvent, reviews_service: ReviewsServiceDep):
    await reviews_service.evaluate_runs_by_hash_if_needed(
        task_id=event.task_id,
        task_schema_id=event.task_schema_id,
        task_input_hash=event.task_input_hash,
        task_output_hash=event.task_output_hash,
        run_id=event.run_id,
        version_id=event.version_id,
        iteration=event.iteration,
        run_failed=event.run_failed,
        input_evaluation_id=event.input_evaluation_id,
        evaluator_id=event.evaluator_id,
    )


JOBS = [trigger_evaluate_run]
