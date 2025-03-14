from api.broker import broker
from api.jobs.common import RunsServiceDep
from core.domain.events import StoreTaskRunEvent


@broker.task(retry_on_error=True)
async def store_task_run(
    event: StoreTaskRunEvent,
    runs_service: RunsServiceDep,
):
    await runs_service.store_task_run(
        event.task,
        event.run,
        event.user_identifier,
        event.trigger,
        event.user_properties.client_source if event.user_properties else None,
    )


JOBS = [store_task_run]
