from pydantic import BaseModel, Field


class UserIdentifier(BaseModel):
    user_id: str | None = Field(default=None)
    user_email: str | None = Field(default=None, description="The user email")


class User(BaseModel):
    """A user from the perspective of the platform"""

    # The old tenant field before migrating to clerk orgs
    tenant: str | None
    sub: str
    org_id: str | None = None
    slug: str | None = None
    user_id: str | None = None
    # The id for an unknown user
    unknown_user_id: str | None = None

    def identifier(self):
        return UserIdentifier(
            user_id=str(self.user_id) if self.user_id else None,
            user_email=self.sub if self.sub else None,
        )
