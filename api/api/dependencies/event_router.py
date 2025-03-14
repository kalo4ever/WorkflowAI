import logging
from typing import Annotated

from fastapi import Depends

from api.dependencies.analytics import (
    AnalyticsOrganizationPropertiesDep,
    AnalyticsTaskPropertiesDep,
    UserPropertiesDep,
)
from api.dependencies.security import FinalTenantDataDep
from api.services.event_handler import tenant_event_router
from core.domain.events import EventRouter

logger = logging.getLogger(__name__)


def event_router_dependency(
    tenant: FinalTenantDataDep,
    user_properties: UserPropertiesDep,
    organization_properties: AnalyticsOrganizationPropertiesDep,
    task_properties: AnalyticsTaskPropertiesDep,
) -> EventRouter:
    return tenant_event_router(tenant.tenant, tenant.uid, user_properties, organization_properties, task_properties)


EventRouterDep = Annotated[EventRouter, Depends(event_router_dependency)]
