from datetime import datetime

from pydantic import BaseModel, Field

from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.users import UserIdentifier
from core.domain.version_environment import VersionEnvironment


class TaskDeployment(BaseModel):
    task_id: str = Field(description="The ID of the task")
    schema_id: int = Field(description="The schema ID of the task")
    # TODO[versionv2]: remove and replace with version_id
    iteration: int = Field(description="The version ID (group iteration or alias)")
    version_id: str = Field(description="The version ID")
    properties: TaskGroupProperties = Field(description="The task group properties")
    environment: VersionEnvironment = Field(description="The deployment environment")

    deployed_at: datetime = Field(description="When the deployment was made")
    deployed_by: UserIdentifier | None = Field(None, description="Who made the deployment")

    def to_task_group(self) -> TaskGroup:
        return TaskGroup(
            iteration=self.iteration,
            properties=self.properties,
        )
