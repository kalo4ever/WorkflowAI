from api.jobs.common import CustomerServiceDep
from core.domain.events import TenantCreatedEvent

from ..broker import broker


@broker.task(retry_on_error=True)
async def handle_tenant_created(event: TenantCreatedEvent, customer_service: CustomerServiceDep):
    await customer_service.handle_customer_created()


JOBS = [handle_tenant_created]
