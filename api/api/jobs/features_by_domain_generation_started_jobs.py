from api.broker import broker
from api.jobs.common import FeatureServiceDep
from core.domain.events import FeaturesByDomainGenerationStarted


@broker.task(retry_on_error=True, max_retries=1)
async def notify_features_by_generation_started(
    event: FeaturesByDomainGenerationStarted,
    feature_service: FeatureServiceDep,
):
    await feature_service.notify_features_by_domain_generation_started(event=event)


JOBS = [notify_features_by_generation_started]
