from api.broker import broker
from api.jobs.common import InternalTasksServiceDep, VersionsServiceDep
from core.domain.events import TaskGroupSaved


@broker.task(retry_on_error=True)
async def generate_changelog(
    event: TaskGroupSaved,
    versions_service: VersionsServiceDep,
    internal_service: InternalTasksServiceDep,
):
    if event.major == 1:
        # First major does not require a changelog since there are no previous major
        return
    if event.minor != 1:
        # Minor is not 1, which means that we probably generated a changelog for this major before
        return

    await versions_service.generate_changelog_for_major(
        task_id=event.task_id,
        schema_id=event.task_schema_id,
        major=event.major,
        properties=event.properties,
        internal_service=internal_service,
    )


JOBS = [generate_changelog]
