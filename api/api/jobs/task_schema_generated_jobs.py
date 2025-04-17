import json
import os
from logging import getLogger
from typing import Any

from api.broker import broker
from api.services import slack_notifications
from core.domain.events import TaskSchemaGeneratedEvent

logger = getLogger(__name__)


def _get_notification_text_content(
    task_name: str,
    version_identifier: str,
    user_request: str,
    assistant_answer: str,
    input_schema: dict[str, Any] | None,
    output_schema: dict[str, Any] | None,
    duration_seconds: float | None = None,
    difference_summary: str | None = None,
) -> str:
    message = f"""New task schema generated with *{version_identifier}*{f" in *{duration_seconds:.2f} seconds*" if duration_seconds else ""}, for task: *{task_name}*

*User message*
```
{user_request}
```

*Assistant answer*
```
{assistant_answer}
```

*Input schema*
```
{json.dumps(input_schema, indent=2) if input_schema else "No input schema"}
```

*Output schema*
```
{json.dumps(output_schema, indent=2) if output_schema else "No output schema"}
```"""

    if difference_summary:
        message += f"""

*Differences summary*
```
{difference_summary}
```
        """

    return message


# TODO: remove ?
@broker.task(retry_on_error=True, max_retries=1)
async def notify_slack_on_task_schema_generated(
    event: TaskSchemaGeneratedEvent,
):
    if os.getenv("SKIP_SLACK_NOTIFICATIONS_FOR_O1_EXPERIMENT", "false").lower() == "true":
        logger.info(
            "Skipping Slack notification for task schema generated event",
        )
        return

    await slack_notifications.send_slack_notification(
        message=_get_notification_text_content(
            task_name=event.updated_task_schema.agent_name,
            version_identifier=event.version_identifier,
            user_request=event.chat_messages[-1].content,
            assistant_answer=event.assistant_answer,
            input_schema=event.updated_task_schema.input_json_schema,
            output_schema=event.updated_task_schema.output_json_schema,
        ),
        user_email=event.user_properties.user_email if event.user_properties else None,
        destination=slack_notifications.SlackNotificationDestination.SCHEMA_GENERATION,
    )


JOBS = [notify_slack_on_task_schema_generated]
