import os

from core.domain.events import Event
from core.storage.slack.utils import get_slack_hyperlink


def get_task_url(event: Event, task_id: str, task_schema_id: int) -> str | None:
    organization_slug = event.organization_properties.organization_slug if event.organization_properties else None
    if organization_slug is None:
        return None

    base_domain = os.environ.get("WORKFLOWAI_APP_URL")
    if base_domain is None:
        return None

    # Not super solid, will break if we change the task URL format in the web app, but we can't access the webapp URL schema from here.
    # Additionally, this code is purely for notification purposes, so it's not critical for the clients
    return f"{base_domain}/{organization_slug}/agents/{task_id}/{task_schema_id}"


def get_task_str_for_slack(event: Event, task_id: str, task_schema_id: int) -> str:
    task_str = task_id
    task_url = get_task_url(event=event, task_id=task_id, task_schema_id=task_schema_id)
    if task_url is not None:
        task_str = get_slack_hyperlink(url=task_url, text=task_str)
    return task_str


def get_task_run_str(event: Event, task_id: str, task_schema_id: int, task_run_id: str) -> str:
    task_run_str = f"task run id:{task_run_id}"
    task_url = get_task_url(
        event=event,
        task_id=task_id,
        task_schema_id=task_schema_id,
    )
    if task_url is None:
        return task_run_str

    return f"{task_url}/runs?taskRunId={task_run_id}"
