from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from core.domain.task_group_properties import TaskGroupProperties
from core.domain.users import UserIdentifier
from core.domain.version_environment import VersionEnvironment
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.task_deployments import TaskDeploymentDocument
from core.storage.mongo.models.user_identifier import UserIdentifierSchema
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_storage_test import TASK_ID
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.task_deployments import MongoTaskDeploymentsStorage
from tests.utils import remove_none


@pytest.fixture(scope="function")
def task_deployments_storage(storage: MongoStorage) -> MongoTaskDeploymentsStorage:
    return storage.task_deployments


def _task_deployment(
    task_id: str = TASK_ID,
    task_schema_id: int = 1,
    iteration: int = 1,
    environment: str = "dev",
    deployed_at: datetime = datetime.now(timezone.utc),
    deployed_by: UserIdentifier = UserIdentifier(user_id="user1", user_email="test@example.com"),
    provider_config_id: str | None = None,
    properties: dict[str, Any] | None = None,
) -> TaskDeploymentDocument:
    # Default properties
    default_properties = {
        "task_id": task_id,
        "task_schema_id": task_schema_id,
        "iteration": iteration,
        "environment": environment,
        "deployed_at": deployed_at,
        "deployed_by": UserIdentifierSchema.from_domain(deployed_by),
        "provider_config_id": provider_config_id,
        "properties": properties or {"instructions": "some instructions", "model": "gemini-1.0-pro-vision-001"},
    }
    # Merge with provided kwargs
    return TaskDeploymentDocument.model_validate(default_properties)


class TestDeployTask:
    async def test_success_one(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        deployment = _task_deployment(
            properties={
                "instructions": "some instructions",
                "model": "gemini-1.0-pro-vision-001",
                "task_variant_id": "hello",
            },
        )
        await task_deployments_storage.deploy_task_version(deployment.to_resource())

        stored = await task_deployments_col.find_one(
            {
                "task_id": TASK_ID,
                "task_schema_id": deployment.task_schema_id,
                "environment": deployment.environment,
                "iteration": deployment.iteration,
            },
        )
        assert stored is not None
        task_deployment_doc = TaskDeploymentDocument.model_validate(stored)
        assert task_deployment_doc is not None
        assert task_deployment_doc.task_id == "task_id"
        assert task_deployment_doc.task_schema_id == 1
        assert task_deployment_doc.iteration == 1
        assert task_deployment_doc.environment == "dev"
        assert abs(task_deployment_doc.deployed_at - deployment.deployed_at).total_seconds() <= 0.001
        assert task_deployment_doc.deployed_by == UserIdentifierSchema(
            user_id="user1",
            user_email="test@example.com",
        )
        assert task_deployment_doc.provider_config_id is None
        assert remove_none(task_deployment_doc.properties) == {
            "has_templated_instructions": False,
            "instructions": "some instructions",
            "model": "gemini-1.0-pro-vision-001",
            "task_variant_id": "hello",
        }

    async def test_success_multiple_same_environment(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        deployment1 = _task_deployment()
        deployment2 = _task_deployment(
            deployed_at=deployment1.deployed_at + timedelta(seconds=5),
            deployed_by=UserIdentifier(user_id="user2", user_email="another@example.com"),
        )
        await task_deployments_storage.deploy_task_version(deployment1.to_resource())
        await task_deployments_storage.deploy_task_version(deployment2.to_resource())

        stored = task_deployments_col.find(
            {
                "task_id": TASK_ID,
                "task_schema_id": deployment1.task_schema_id,
                "iteration": deployment1.iteration,
                "environment": deployment1.environment,
            },
        )

        count = 0
        async for doc in stored:
            task_deployment_doc = TaskDeploymentDocument.model_validate(doc)
            assert task_deployment_doc is not None
            assert task_deployment_doc.task_id == "task_id"
            assert task_deployment_doc.task_schema_id == 1
            assert task_deployment_doc.iteration == 1
            assert task_deployment_doc.environment == "dev"
            assert task_deployment_doc.deployed_by == UserIdentifierSchema(
                user_id="user2",
                user_email="another@example.com",
            )
            assert remove_none(task_deployment_doc.properties) == {
                "has_templated_instructions": False,
                "instructions": "some instructions",
                "model": "gemini-1.0-pro-vision-001",
            }
            count += 1
        assert count == 1

    async def test_success_multiple_different_environment(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        deployment1 = _task_deployment()
        deployment2 = _task_deployment(
            deployed_at=deployment1.deployed_at + timedelta(seconds=5),
            deployed_by=UserIdentifier(user_id="user2", user_email="another@example.com"),
            environment="staging",
        )
        await task_deployments_storage.deploy_task_version(deployment1.to_resource())
        await task_deployments_storage.deploy_task_version(deployment2.to_resource())

        stored = task_deployments_col.find(
            {
                "task_id": TASK_ID,
                "task_schema_id": deployment1.task_schema_id,
                "iteration": deployment1.iteration,
            },
        )

        count = 0
        async for doc in stored:
            task_deployment_doc = TaskDeploymentDocument.model_validate(doc)
            assert task_deployment_doc is not None
            assert task_deployment_doc.task_id == "task_id"
            assert task_deployment_doc.task_schema_id == 1
            assert task_deployment_doc.iteration == 1
            assert task_deployment_doc.environment in ("dev", "staging")
            assert task_deployment_doc.deployed_by in (
                UserIdentifierSchema(
                    user_id="user2",
                    user_email="another@example.com",
                ),
                UserIdentifierSchema(
                    user_id="user1",
                    user_email="test@example.com",
                ),
            )
            assert remove_none(task_deployment_doc.properties) == {
                "has_templated_instructions": False,
                "instructions": "some instructions",
                "model": "gemini-1.0-pro-vision-001",
            }
            count += 1
        assert count == 2


class TestListDeployments:
    async def test_success(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        deployment = _task_deployment()
        await task_deployments_storage.deploy_task_version(deployment.to_resource())

        deployments = [d async for d in task_deployments_storage.list_task_deployments(TASK_ID, 1)]
        assert len(deployments) == 1
        assert deployments[0].task_id == "task_id"
        assert deployments[0].schema_id == 1
        assert deployments[0].iteration == 1
        assert deployments[0].environment == "dev"
        assert abs(deployments[0].deployed_at - deployment.deployed_at).total_seconds() <= 0.001
        assert deployments[0].deployed_by == UserIdentifier(
            user_id="user1",
            user_email="test@example.com",
        )
        assert deployments[0].provider_config_id is None
        assert deployments[0].properties == TaskGroupProperties.model_validate(
            {"instructions": "some instructions", "model": "gemini-1.0-pro-vision-001"},
        )

    async def test_not_found(self, task_deployments_storage: MongoTaskDeploymentsStorage) -> None:
        deployments = [d async for d in task_deployments_storage.list_task_deployments(TASK_ID, 1)]
        assert len(deployments) == 0

    async def test_update_existing_provider_config_id(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
    ) -> None:
        # Insert initial deployment
        initial = _task_deployment()
        await task_deployments_storage.deploy_task_version(initial.to_resource())

        # Create updated deployment
        updated = _task_deployment(
            deployed_by=UserIdentifier(user_id="user2", user_email="another@example.com"),
            provider_config_id="config1",
            deployed_at=initial.deployed_at + timedelta(seconds=5),
        )
        await task_deployments_storage.deploy_task_version(updated.to_resource())

        # Verify update
        stored = task_deployments_storage.list_task_deployments(
            initial.task_id,
            initial.task_schema_id,
            VersionEnvironment(initial.environment),
            initial.iteration,
        )
        stored_deployments = [d async for d in stored]
        assert len(stored_deployments) == 1
        assert stored_deployments[0].iteration == 1
        assert stored_deployments[0].environment == "dev"
        assert abs(stored_deployments[0].deployed_at - updated.deployed_at).total_seconds() <= 0.001
        assert stored_deployments[0].deployed_by is not None
        assert stored_deployments[0].deployed_by.user_id == "user2"
        assert stored_deployments[0].deployed_by.user_email == "another@example.com"
        assert stored_deployments[0].provider_config_id == "config1"
        assert stored_deployments[0].properties == TaskGroupProperties.model_validate(
            {"instructions": "some instructions", "model": "gemini-1.0-pro-vision-001"},
        )

    async def test_exclude_properties(self, task_deployments_storage: MongoTaskDeploymentsStorage) -> None:
        # Check there are no validation errors when excluding properties
        deployment = _task_deployment()
        await task_deployments_storage.deploy_task_version(deployment.to_resource())

        deployments = [
            d async for d in task_deployments_storage.list_task_deployments(TASK_ID, 1, exclude=["properties"])
        ]
        assert len(deployments) == 1


class TestGetDeployment:
    async def test_success(self, task_deployments_storage: MongoTaskDeploymentsStorage) -> None:
        deployment = _task_deployment()
        await task_deployments_storage.deploy_task_version(deployment.to_resource())

        stored = await task_deployments_storage.get_task_deployment(TASK_ID, 1, VersionEnvironment.DEV)
        assert stored is not None
        assert stored.task_id == "task_id"
        assert stored.schema_id == 1
        assert stored.iteration == 1
        assert stored.environment == "dev"

    async def test_not_found(self, task_deployments_storage: MongoTaskDeploymentsStorage) -> None:
        with pytest.raises(ObjectNotFoundException):
            await task_deployments_storage.get_task_deployment(TASK_ID, 1, VersionEnvironment.DEV)


class TestGetTaskDeploymentForIteration:
    async def test_success(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        # Create deployments for the same iteration but different environments
        deployment1 = _task_deployment(environment="dev")
        deployment2 = _task_deployment(
            deployed_at=deployment1.deployed_at + timedelta(seconds=5),
            environment="staging",
        )
        await task_deployments_storage.deploy_task_version(deployment1.to_resource())
        await task_deployments_storage.deploy_task_version(deployment2.to_resource())

        # Get deployments for iteration 1
        deployments = [d async for d in task_deployments_storage.get_task_deployment_for_iteration(TASK_ID, 1)]
        assert len(deployments) == 2

        # Verify both deployments are returned
        environments = {d.environment for d in deployments}
        assert environments == {"dev", "staging"}

        # Verify deployment details
        for deployment in deployments:
            assert deployment.task_id == TASK_ID
            assert deployment.schema_id == 1
            assert deployment.iteration == 1
            assert deployment.properties == TaskGroupProperties.model_validate(
                {"instructions": "some instructions", "model": "gemini-1.0-pro-vision-001"},
            )

    async def test_different_iterations(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        # Create deployments for different iterations
        deployment1 = _task_deployment(iteration=1)
        deployment2 = _task_deployment(
            iteration=2,
            environment="staging",
            deployed_at=deployment1.deployed_at + timedelta(seconds=5),
        )
        await task_deployments_storage.deploy_task_version(deployment1.to_resource())
        await task_deployments_storage.deploy_task_version(deployment2.to_resource())

        # Get deployments for iteration 1
        deployments1 = [d async for d in task_deployments_storage.get_task_deployment_for_iteration(TASK_ID, 1)]
        assert len(deployments1) == 1
        assert deployments1[0].iteration == 1

        # Get deployments for iteration 2
        deployments2 = [d async for d in task_deployments_storage.get_task_deployment_for_iteration(TASK_ID, 2)]
        assert len(deployments2) == 1
        assert deployments2[0].iteration == 2

    async def test_not_found(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
    ) -> None:
        # Get deployments for non-existent iteration
        deployments = [d async for d in task_deployments_storage.get_task_deployment_for_iteration(TASK_ID, 999)]
        assert len(deployments) == 0

    async def test_different_task_ids(
        self,
        task_deployments_storage: MongoTaskDeploymentsStorage,
        task_deployments_col: AsyncCollection,
    ) -> None:
        # Create deployments for different task IDs but same iteration
        deployment1 = _task_deployment(task_id="task1", iteration=1)
        deployment2 = _task_deployment(
            task_id="task2",
            iteration=1,
            deployed_at=deployment1.deployed_at + timedelta(seconds=5),
        )
        await task_deployments_storage.deploy_task_version(deployment1.to_resource())
        await task_deployments_storage.deploy_task_version(deployment2.to_resource())

        # Get deployments for task1
        deployments1 = [d async for d in task_deployments_storage.get_task_deployment_for_iteration("task1", 1)]
        assert len(deployments1) == 1
        assert deployments1[0].task_id == "task1"

        # Get deployments for task2
        deployments2 = [d async for d in task_deployments_storage.get_task_deployment_for_iteration("task2", 1)]
        assert len(deployments2) == 1
        assert deployments2[0].task_id == "task2"
