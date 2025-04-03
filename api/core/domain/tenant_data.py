from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from core.domain.models import Provider
from core.providers.base.config import ProviderConfig


class ProviderSettings(BaseModel):
    id: str
    created_at: datetime
    provider: Provider
    preserve_credits: bool | None = None

    def decrypt(self) -> ProviderConfig:
        # Implement decryption in subclasses
        raise NotImplementedError()


class PublicOrganizationData(BaseModel):
    uid: int = 0  # will be filled by storage
    tenant: str = ""
    slug: str = ""
    name: str | None = None
    org_id: str | None = None
    owner_id: str | None = None


class TenantData(PublicOrganizationData):
    owner_id: str | None = Field(default=None, title="Owner id")
    anonymous_user_id: str | None = Field(default=None, title="Anonymous user id")
    anonymous: bool | None = Field(default=None, title="Anonymous organization")
    stripe_customer_id: str | None = None
    providers: list[ProviderSettings] = Field(default_factory=list, title="List of provider configurations")
    added_credits_usd: float = Field(default=0.0, title="Total credits added to the organization")
    current_credits_usd: float = Field(default=0.0, title="Current credits available to the organization")
    locked_for_payment: bool | None = None

    automatic_payment_enabled: bool = Field(default=False, title="Automatic payment enabled")
    automatic_payment_threshold: float | None = Field(default=None, title="Automatic payment threshold")
    automatic_payment_balance_to_maintain: float | None = Field(
        default=None,
        title="Automatic payment balance to maintain",
    )
    feedback_slack_hook: str | None = Field(default=None, title="Slack webhook URL for feedback notifications")

    class PaymentFailure(BaseModel):
        failure_date: datetime
        failure_code: Literal["payment_failed", "internal"]
        failure_reason: str

    payment_failure: PaymentFailure | None = None
