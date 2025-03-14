import logging
import os
from datetime import datetime
from typing import Callable, Protocol, override

from core.domain.analytics_events.analytics_events import (
    AnalyticsEvent,
    EventProperties,
    FullAnalyticsEvent,
    OrganizationProperties,
    TaskProperties,
    UserProperties,
)
from core.domain.events import EventRouter, SendAnalyticsEvent
from core.utils.fields import datetime_factory


class AnalyticsService(Protocol):
    def send_event(
        self,
        builder: Callable[[], EventProperties],
        time: datetime | None = None,
        task_properties: Callable[[], TaskProperties] | None = None,
        organization_properties: Callable[[], OrganizationProperties] | None = None,
    ) -> None: ...


class DefaultAnalyticsService(AnalyticsService):
    def __init__(
        self,
        user_properties: UserProperties | None,
        organization_properties: OrganizationProperties | None,
        task_properties: TaskProperties | None,
        event_router: EventRouter,
    ):
        self.user_properties = user_properties
        self.organization_properties = organization_properties
        self.event_router = event_router
        self.task_properties = task_properties
        self._logger = logging.getLogger(self.__class__.__name__)

    def _build_organization(self, builder: Callable[[], OrganizationProperties] | None = None):
        if builder:
            return builder()
        return self.organization_properties or OrganizationProperties(tenant="unknown")

    @override
    def send_event(
        self,
        builder: Callable[[], EventProperties],
        time: datetime | None = None,
        task_properties: Callable[[], TaskProperties] | None = None,
        organization_properties: Callable[[], OrganizationProperties] | None = None,
    ):
        try:
            full = FullAnalyticsEvent(
                user_properties=self.user_properties,
                organization_properties=self._build_organization(organization_properties),
                task_properties=task_properties() if task_properties else self.task_properties,
                event=AnalyticsEvent(event_properties=builder(), time=time or datetime_factory()),
            )
            self.event_router(SendAnalyticsEvent(event=full))
        except Exception:
            self._logger.exception("Failed to build analytics event")
            return


class NoopAnalyticsService(AnalyticsService):
    """An analytics service that does nothing. Used when skipping users"""

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    @override
    def send_event(
        self,
        builder: Callable[[], EventProperties],
        time: datetime | None = None,
        task_properties: Callable[[], TaskProperties] | None = None,
        organization_properties: Callable[[], OrganizationProperties] | None = None,
    ):
        self._logger.debug("Skipping analytics event")


_BLACKLISTED_ORG_IDS = {
    *os.getenv("ANALYTICS_BLACKLISTED_ORGS", "").split(","),
}


def analytics_service(
    user_properties: UserProperties | None,
    organization_properties: OrganizationProperties | None,
    task_properties: TaskProperties | None,
    event_router: EventRouter,
) -> AnalyticsService:
    if organization_properties and organization_properties.organization_id in _BLACKLISTED_ORG_IDS:
        return NoopAnalyticsService()
    return DefaultAnalyticsService(user_properties, organization_properties, task_properties, event_router)
