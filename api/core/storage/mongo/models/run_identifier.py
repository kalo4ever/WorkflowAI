from pydantic import BaseModel

from core.domain.run_identifier import RunIdentifier as DomainRunIdentifier
from core.domain.users import UserIdentifier


class RunIdentifier(BaseModel):
    tenant: str | None = None
    task_id: str | None = None
    task_schema_id: int | None = None
    run_id: str | None = None

    @classmethod
    def from_domain(cls, run_identifier: DomainRunIdentifier):
        return cls(
            tenant=run_identifier.tenant,
            task_id=run_identifier.task_id,
            task_schema_id=run_identifier.task_schema_id,
            run_id=run_identifier.run_id,
        )

    def to_domain(self):
        return DomainRunIdentifier(
            tenant=self.tenant or "",
            task_id=self.task_id or "",
            task_schema_id=self.task_schema_id or 0,
            run_id=self.run_id or "",
        )


class RunOrUserIdentifier(BaseModel):
    tenant: str | None = None
    task_id: str | None = None
    task_schema_id: int | None = None
    run_id: str | None = None
    user_id: str | None = None
    user_email: str | None = None

    @classmethod
    def from_domain(cls, run_or_user_identifier: DomainRunIdentifier | UserIdentifier):
        if isinstance(run_or_user_identifier, UserIdentifier):
            return cls(user_id=run_or_user_identifier.user_id, user_email=run_or_user_identifier.user_email)
        return cls(
            tenant=run_or_user_identifier.tenant,
            task_id=run_or_user_identifier.task_id,
            task_schema_id=run_or_user_identifier.task_schema_id,
            run_id=run_or_user_identifier.run_id,
        )

    def to_domain(self) -> DomainRunIdentifier | UserIdentifier:
        if self.user_id:
            return UserIdentifier(user_id=self.user_id, user_email=self.user_email)
        return DomainRunIdentifier(
            tenant=self.tenant or "",
            task_id=self.task_id or "",
            task_schema_id=self.task_schema_id or 0,
            run_id=self.run_id or "",
        )
