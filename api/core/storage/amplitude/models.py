from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from core.domain.analytics_events.analytics_events import (
    FullAnalyticsEvent,
)


class AmplitudeEvent(BaseModel):
    user_id: str
    event_type: str
    time: int
    event_properties: dict[str, Any]
    user_properties: dict[str, Any]
    insert_id: str

    @classmethod
    def from_domain(cls, event: FullAnalyticsEvent):
        event_properties = event.event.event_properties.model_dump(exclude_none=True, exclude={"event_type"})
        if event.user_properties:
            event_properties["user"] = event.user_properties.model_dump(exclude_none=True)
        if event.task_properties:
            event_properties["task"] = event.task_properties.model_dump(exclude_none=True)
        return cls(
            # This means that the user id will change once an organization is created
            user_id=event.organization_properties.tenant,
            event_type=event.event.event_properties.event_type,
            time=int(event.event.time.timestamp() * 1000),
            event_properties=event_properties,
            user_properties=event.organization_properties.model_dump(exclude={"tenant"}, exclude_none=True),
            insert_id=event.event.insert_id,
        )


class AmplitudeRequest(BaseModel):
    api_key: str

    events: list[AmplitudeEvent]

    @classmethod
    def from_domain(cls, api_key: str, events: Iterable[FullAnalyticsEvent]):
        return cls(
            api_key=api_key,
            events=[AmplitudeEvent.from_domain(event) for event in events],
        )
