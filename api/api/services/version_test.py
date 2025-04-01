from datetime import datetime
from typing import AsyncIterator, TypeVar
from unittest.mock import AsyncMock, Mock

import pytest

from api.services.versions import VersionsService
from core.domain.changelogs import VersionChangelog
from core.domain.events import TaskGroupSaved
from core.domain.models import Model
from core.domain.task_deployment import TaskDeployment
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.users import UserIdentifier
from core.domain.version_environment import VersionEnvironment
from core.domain.version_major import (
    VersionMajor,
)

T = TypeVar("T")


async def mock_aiter(*args: T) -> AsyncIterator[T]:
    for arg in args:
        yield arg


@pytest.fixture
def versions_service(mock_storage: Mock, mock_event_router: Mock) -> VersionsService:
    return VersionsService(mock_storage, mock_event_router)


class TestListVersionMajors:
    async def test_list_version_majors(self, versions_service: VersionsService, mock_storage: Mock):
        # Setup test data
        task_id = "test_task"
        schema_id = 1

        # Mock version majors
        version = VersionMajor(
            major=1,
            schema_id=schema_id,
            similarity_hash="hash1",
            created_at=datetime.now(),
            properties=VersionMajor.Properties(
                temperature=0.7,
                instructions="test instructions",
            ),
            minors=[
                VersionMajor.Minor(
                    id="test_id",
                    iteration=1,
                    minor=1,
                    properties=VersionMajor.Minor.Properties(
                        model=Model.GPT_4O_LATEST,
                    ),
                ),
            ],
        )
        mock_storage.task_groups.list_version_majors.return_value = mock_aiter(version)

        # Mock deployments
        deployment = TaskDeployment(
            task_id=task_id,
            schema_id=schema_id,
            iteration=1,
            version_id="1",
            deployed_at=datetime.now(),
            deployed_by=UserIdentifier(user_email="test@example.com"),
            environment=VersionEnvironment.DEV,
            properties=TaskGroupProperties(),
        )
        mock_storage.task_deployments.list_task_deployments.return_value = mock_aiter(deployment)

        # Mock changelogs
        changelog = VersionChangelog(
            task_id=task_id,
            task_schema_id=schema_id,
            major_from=1,
            major_to=2,
            similarity_hash_from="hash0",
            similarity_hash_to="hash1",
            changelog=["test change"],
        )
        mock_storage.changelogs.list_changelogs.return_value = mock_aiter(changelog)

        # Mock models service
        mock_models_service = Mock()
        mock_models_service.model_price_calculator = AsyncMock(return_value=lambda _model: 0.01)  # pyright: ignore [reportUnknownLambdaType]

        # Execute
        result = await versions_service.list_version_majors((task_id, 1), schema_id, mock_models_service)

        # Verify
        assert len(result) == 1
        assert result[0].schema_id == schema_id
        assert result[0].similarity_hash == "hash1"
        assert result[0].changelog == changelog
        assert len(result[0].minors) == 1
        assert result[0].minors[0].iteration == 1
        assert result[0].minors[0].deployments
        assert result[0].minors[0].deployments[0].environment == "dev"
        assert result[0].minors[0].cost_estimate_usd == 0.01

        # Verify calls
        mock_storage.task_groups.list_version_majors.assert_called_once_with(task_id, schema_id)
        mock_storage.task_deployments.list_task_deployments.assert_called_once_with(
            task_id,
            schema_id,
            exclude=["properties"],
        )
        mock_storage.changelogs.list_changelogs.assert_called_once_with(task_id, schema_id)
        mock_models_service.model_price_calculator.assert_called_once_with((task_id, 1), schema_id)


class TestSaveVersion:
    async def test_save_version_newly_saved(
        self,
        versions_service: VersionsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        # Setup test data
        task_id = "test_task"
        hash = "test_hash"
        task_group = Mock(
            schema_id=1,
            semver=Mock(major=1, minor=1),
            properties=TaskGroupProperties(
                temperature=0.5,
                instructions="New instructions",
            ),
        )
        mock_storage.task_groups.save_task_group.return_value = (task_group, True)

        # Execute
        result = await versions_service.save_version(task_id, hash)

        # Verify
        assert result == task_group
        mock_storage.task_groups.save_task_group.assert_called_once_with(task_id, hash)
        mock_event_router.assert_called_once_with(
            TaskGroupSaved(
                task_id=task_id,
                task_schema_id=task_group.schema_id,
                hash=hash,
                major=task_group.semver.major,
                minor=task_group.semver.minor,
                properties=task_group.properties,
            ),
        )

    async def test_save_version_not_newly_saved(
        self,
        versions_service: VersionsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        # Setup test data
        task_id = "test_task"
        hash = "test_hash"
        task_group = Mock(schema_id=1, semver=Mock(major=1, minor=1))
        mock_storage.task_groups.save_task_group.return_value = (task_group, False)

        # Execute
        result = await versions_service.save_version(task_id, hash)

        # Verify
        assert result == task_group
        mock_storage.task_groups.save_task_group.assert_called_once_with(task_id, hash)
        mock_event_router.assert_not_called()
