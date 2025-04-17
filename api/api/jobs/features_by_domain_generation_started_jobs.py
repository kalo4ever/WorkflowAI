from api.broker import broker
from api.jobs.common import CustomerServiceDep
from core.domain.events import FeaturesByDomainGenerationStarted


@broker.task(retry_on_error=True, max_retries=1)
async def notify_features_by_generation_started(
    event: FeaturesByDomainGenerationStarted,
    customer_service: CustomerServiceDep,
):
    await customer_service.notify_features_by_domain_generation_started(event=event)


JOBS = [notify_features_by_generation_started]
