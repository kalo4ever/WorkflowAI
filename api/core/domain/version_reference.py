from typing import Any, Optional, Self

from pydantic import BaseModel, Field, model_validator

from core.domain.task_group import TaskGroupIdentifier
from core.domain.version_environment import VersionEnvironment

from .task_group_properties import TaskGroupProperties


class VersionReference(BaseModel):
    """Refer to an existing group or create a new one with the given properties.
    Only one of id, iteration or properties must be provided"""

    version: int | VersionEnvironment | TaskGroupIdentifier | None = None

    properties: Optional[TaskGroupProperties] = Field(
        description="The properties to evaluate the task schema with. A group will be created if needed",
        default=None,
    )

    is_external: Optional[bool] = Field(
        description="Whether the group is external, i-e not created by internal runners",
        default=None,
    )

    @model_validator(mode="after")
    def post_validate(self) -> Self:
        count = sum(1 for x in [self.version, self.properties] if x)
        if count != 1:
            raise ValueError("Exactly one of version, properties must be provided")
        return self

    # TODO: use unpack when supported -> https://github.com/pydantic/pydantic/discussions/7915
    @classmethod
    def with_properties(
        cls,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        instructions: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> "VersionReference":
        """Short hand for creating a VersionReference with properties."""
        return VersionReference(
            properties=TaskGroupProperties(
                model=model,
                provider=provider,
                temperature=temperature,
                instructions=instructions,
                max_tokens=max_tokens,
                **kwargs,
            ),
        )
