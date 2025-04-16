import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.dependencies.provider_factory import ProviderFactoryDep
from api.dependencies.security import RequiredUserOrganizationDep
from api.dependencies.storage import OrganizationStorageDep
from api.tags import RouteTags
from core.domain.models.providers import Provider
from core.domain.tenant_data import (
    ProviderConfig,
    ProviderSettings,
    TenantData,
)
from core.utils.iter_utils import safe_map_optional

router = APIRouter(prefix="/organization", tags=[RouteTags.ORGANIZATIONS])

_logger = logging.getLogger(__name__)


class OrganizationResponse(BaseModel):
    uid: int = 0  # will be filled by storage
    tenant: str = ""
    slug: str = ""
    name: str | None = None
    org_id: str | None = None
    owner_id: str | None = None

    stripe_customer_id: str | None

    class ConfiguredProvider(BaseModel):
        id: str
        created_at: datetime
        provider: Provider

        @classmethod
        def from_domain(cls, provider: ProviderSettings):
            return cls(
                id=provider.id,
                created_at=provider.created_at,
                provider=provider.provider,
            )

    providers: list[ConfiguredProvider] | None

    current_credits_usd: float

    automatic_payment_enabled: bool
    automatic_payment_threshold: float | None
    automatic_payment_balance_to_maintain: float | None

    class PaymentFailure(BaseModel):
        failure_date: datetime
        failure_code: Literal["payment_failed", "internal"]
        failure_reason: str

        @classmethod
        def from_domain(cls, payment_failure: TenantData.PaymentFailure):
            return cls(
                failure_date=payment_failure.failure_date,
                failure_code=payment_failure.failure_code,
                failure_reason=payment_failure.failure_reason,
            )

    payment_failure: PaymentFailure | None = None

    @classmethod
    def from_domain(cls, tenant: TenantData):
        return cls(
            uid=tenant.uid,
            tenant=tenant.tenant,
            slug=tenant.slug,
            name=tenant.name,
            org_id=tenant.org_id,
            owner_id=tenant.owner_id,
            stripe_customer_id=tenant.stripe_customer_id,
            providers=safe_map_optional(tenant.providers, cls.ConfiguredProvider.from_domain),
            current_credits_usd=tenant.current_credits_usd,
            automatic_payment_enabled=tenant.automatic_payment_enabled,
            automatic_payment_threshold=tenant.automatic_payment_threshold,
            automatic_payment_balance_to_maintain=tenant.automatic_payment_balance_to_maintain,
            payment_failure=cls.PaymentFailure.from_domain(tenant.payment_failure) if tenant.payment_failure else None,
        )


@router.get("/settings", description="List settings for a tenant")
async def get_organization_settings(tenant: RequiredUserOrganizationDep) -> OrganizationResponse:
    return OrganizationResponse.from_domain(tenant)


@router.post("/settings/providers", description="Add a provider config")
async def add_provider_settings(
    request: ProviderConfig,
    storage: OrganizationStorageDep,
    provider_factory: ProviderFactoryDep,
) -> ProviderSettings:
    provider_cls = provider_factory.provider_type(request)
    # Will raise InvalidProviderConfig if the config is invalid
    config = provider_cls.sanitize_config(request)

    provider = provider_cls(config, config_id="temp")

    is_valid = await provider.check_valid()
    if not is_valid:
        raise HTTPException(400, "Invalid provider config")

    return await storage.add_provider_config(config)


@router.delete("/settings/providers/{provider_id}", description="Delete a provider config")
async def delete_provider_settings(provider_id: str, storage: OrganizationStorageDep) -> None:
    await storage.delete_provider_config(provider_id)
