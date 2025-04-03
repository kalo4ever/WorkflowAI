from collections.abc import AsyncIterator, Iterable
from typing import Protocol

from core.domain.task_deployment import TaskDeployment
from core.domain.version_environment import VersionEnvironment
from core.storage.mongo.models.deployment_document import TaskDeploymentDocument


class TaskDeploymentsStorage(Protocol):
    def list_task_deployments(
        self,
        task_id: str,
        task_schema_id: int | None = None,
        environment: VersionEnvironment | None = None,
        iteration: int | None = None,
        exclude: Iterable[str] | None = None,
    ) -> AsyncIterator[TaskDeployment]: ...

    async def get_task_deployment(
        self,
        task_id: str,
        task_schema_id: int,
        environment: VersionEnvironment,
    ) -> TaskDeployment: ...

    def get_task_deployment_for_iteration(self, task_id: str, iteration: int) -> AsyncIterator[TaskDeployment]: ...

    async def deploy_task_version(self, deployment: TaskDeployment) -> TaskDeploymentDocument: ...

    async def get_task_deployed_versions_ids(self, task_id: str) -> set[int]: ...
