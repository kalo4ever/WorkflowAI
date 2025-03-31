from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel

from api.jobs.common import StorageDep
from api.services.analytics import AnalyticsService
from api.services.groups import GroupService
from api.services.run import RunService
from core.domain.analytics_events.analytics_events import DeployedTaskVersionProperties, VersionProperties
from core.domain.errors import BadRequestError, ProviderError
from core.domain.task_group import TaskGroup, TaskGroupQuery
from core.domain.task_run_query import SerializableTaskRunQuery
from core.domain.tenant_data import ProviderSettings
from core.domain.users import UserIdentifier
from core.domain.version_environment import VersionEnvironment
from core.domain.version_reference import VersionReference
from core.storage import TaskTuple
from core.storage.mongo.models.task_deployments import TaskDeployment


class VersionsResponse(TaskGroup):
    # Add directly to SerializableTaskVariant after ClickHouse migration?
    recent_runs_count: int = 0

    @classmethod
    def from_domain(cls, item: TaskGroup) -> Self:
        return cls(**item.model_dump())


class DeployedVersionsResponse(VersionsResponse):
    class Deployment(BaseModel):
        environment: VersionEnvironment
        provider_config_id: str | None = None
        deployed_at: datetime
        deployed_by: UserIdentifier | None = None

    deployments: list[Deployment] | None = None

    @classmethod
    def from_domain(cls, item: TaskGroup) -> Self:
        return cls(**item.model_dump())


class TaskDeploymentsService:
    def __init__(
        self,
        storage: StorageDep,
        run_service: RunService,
        group_service: GroupService,
        analytics_service: AnalyticsService,
    ):
        self._storage_deployments = storage.task_deployments
        self._storage_task_groups = storage.task_groups
        self._storage = storage
        self._run_service = run_service
        self._group_service = group_service
        self._analytics_service = analytics_service

    async def validate_provider_config_id_for_version(
        self,
        task_id: TaskTuple,
        task_schema_id: int,
        version_id: int,
        provider_config_id: str,
        provider_settings: list[ProviderSettings] | None,
    ):
        q = SerializableTaskRunQuery(
            task_id=task_id[0],
            task_schema_id=task_schema_id,
            include_fields={"_id", "task_input"},
        )
        # 1. Retrive latest successful task run for this version
        try:
            latest_run = await anext(self._storage.task_runs.fetch_task_run_resources(task_id[1], q))
        except StopAsyncIteration:
            # No runs yet for this version, so can't validate
            return

        if not latest_run:
            return
        # 2. Re-run this task run with new provider_config
        _runner, _ = await self._group_service.sanitize_groups_for_internal_runner(
            task_id[0],
            task_schema_id,
            VersionReference(version=version_id),
            provider_config_id=provider_config_id,
            disable_fallback=True,
            provider_settings=provider_settings,
        )

        try:
            await self._run_service.run(
                runner=_runner,
                task_run_id=latest_run.id,
                stream_serializer=None,
                cache="never",
                labels=set(),
                metadata=None,
                trigger="internal",
                task_input=latest_run.task_input,
                store_inline=False,
                file_storage=None,
                serializer=lambda run: run,
            )
        except ProviderError:
            raise BadRequestError(
                msg="The provider config did not run on the given task",
            )
        return

    async def deploy_version(
        self,
        task_id: TaskTuple,
        task_schema_id: int,
        version_id: int,
        environment: VersionEnvironment,
        provider_config_id: str | None,
        deployed_by: UserIdentifier | None,
        provider_settings: list[ProviderSettings] | None,
    ) -> TaskDeployment:
        group = await self._storage_task_groups.get_task_group_by_iteration(task_id[0], task_schema_id, version_id)

        task_deployment = TaskDeployment(
            task_id=task_id[0],
            schema_id=task_schema_id,
            iteration=version_id,
            environment=environment,
            provider_config_id=provider_config_id,
            deployed_by=deployed_by,
            deployed_at=datetime.now(timezone.utc),
            properties=group.properties,
        )
        if provider_config_id:
            await self.validate_provider_config_id_for_version(
                task_id,
                task_schema_id,
                version_id,
                provider_config_id,
                provider_settings,
            )

        self._analytics_service.send_event(
            lambda: DeployedTaskVersionProperties(
                group=VersionProperties.from_domain(group),
                environment=environment,
            ),
        )

        updated_doc = await self._storage_deployments.deploy_task_version(task_deployment)
        return updated_doc.to_resource()

    async def _collect_groups(self, task_id: str, deployed_versions_ids: set[int]) -> list[TaskGroup]:
        return [
            group
            async for group in self._storage_task_groups.list_task_groups(
                TaskGroupQuery(task_id=task_id, iterations=deployed_versions_ids),
            )
        ]

    async def get_task_deployments(
        self,
        task_id: str,
    ) -> list[DeployedVersionsResponse]:
        deployed_versions_ids = await self._storage_deployments.get_task_deployed_versions_ids(task_id)

        all_deployments_in_task = self._storage_deployments.list_task_deployments(task_id)

        groups = await self._collect_groups(task_id, deployed_versions_ids)

        deps_by_version: dict[int, list[TaskDeployment]] = {}
        async for deployment in all_deployments_in_task:
            deps_by_version.setdefault(deployment.iteration, []).append(deployment)

        return [
            DeployedVersionsResponse(
                **group.model_dump(),
                deployments=[
                    DeployedVersionsResponse.Deployment(
                        environment=d.environment,
                        provider_config_id=d.provider_config_id,
                        deployed_at=d.deployed_at,
                        deployed_by=d.deployed_by,
                    )
                    for d in deps_by_version[group.iteration]
                ],
            )
            for group in groups
            if group.iteration in deps_by_version
        ]
