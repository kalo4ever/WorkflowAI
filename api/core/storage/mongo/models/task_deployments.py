from datetime import datetime
from typing import Any, Literal, Self

from pydantic import Field

from core.domain.task_deployment import TaskDeployment
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.version_environment import VersionEnvironment
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.user_identifier import UserIdentifierSchema
from core.utils.fields import datetime_factory


class TaskDeploymentDocument(BaseDocumentWithID):
    task_id: str = Field(..., description="The ID of the task")
    task_schema_id: int = Field(default=0, description="The schema ID of the task")
    # TODO[versionv2]: replace with hash
    iteration: int = Field(default=0, description="The version ID (group iteration or alias)")
    environment: Literal["dev", "staging", "production"] = Field(..., description="The deployment environment")
    provider_config_id: str | None = Field(default=None, description="The provider configuration ID")
    deployed_at: datetime = Field(default_factory=datetime_factory, description="When the deployment was made")
    deployed_by: UserIdentifierSchema | None = Field(default=None, description="Who made the deployment")
    properties: dict[str, Any] | None = Field(default=None, description="The task group properties")

    @classmethod
    def from_resource(cls, tenant: str, deployment: TaskDeployment) -> Self:
        return cls(
            tenant=tenant,
            task_id=deployment.task_id,
            task_schema_id=deployment.schema_id,
            iteration=deployment.iteration,
            environment=deployment.environment.value,
            provider_config_id=deployment.provider_config_id,
            deployed_at=deployment.deployed_at,
            deployed_by=UserIdentifierSchema.from_domain(deployment.deployed_by) if deployment.deployed_by else None,
            properties=deployment.properties.model_dump() if deployment.properties else None,
        )

    def to_resource(self) -> TaskDeployment:
        return TaskDeployment(
            task_id=self.task_id,
            schema_id=self.task_schema_id,
            iteration=self.iteration,
            environment=VersionEnvironment(self.environment),
            provider_config_id=self.provider_config_id,
            deployed_at=self.deployed_at,
            deployed_by=self.deployed_by.to_domain() if self.deployed_by else None,
            # properties can be empty when projected out
            properties=TaskGroupProperties.model_validate(self.properties or {}),
        )

    def set_value(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "provider_config_id": self.provider_config_id,
            "properties": self.properties,
            "deployed_by": self.deployed_by.model_dump() if self.deployed_by else None,
            "deployed_at": self.deployed_at,
        }
