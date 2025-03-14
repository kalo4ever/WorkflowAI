from api.jobs.common import BackgroundRunServiceDep
from core.domain.events import TriggerTaskRunEvent

from ..broker import broker


@broker.task(retry_on_error=True)
async def trigger_run(event: TriggerTaskRunEvent, run_service: BackgroundRunServiceDep):
    await run_service.run_for_trigger(
        task_id=event.task_id,
        task_schema_id=event.task_schema_id,
        task_input=event.task_input,
        task_input_hash=event.task_input_hash,
        group_iteration=event.group_iteration,
        run_id=event.run_id,
        trigger=event.trigger,
        retry_count=event.retry_count,
    )
