from datetime import datetime

from core.domain.task_deployment import TaskDeployment
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.users import UserIdentifier
from core.domain.version_environment import VersionEnvironment
from core.storage.mongo.models.task_deployments import TaskDeploymentDocument


class TestTaskDeploymentsConversion:
    def test_task_variant_id(self):
        properties = TaskGroupProperties.model_validate(
            {
                "model": "gpt-4o-2024-11-20",
                "task_variant_id": "123",
            },
        )
        deployment = TaskDeployment(
            task_id="123",
            schema_id=1,
            iteration=1,
            properties=properties,
            environment=VersionEnvironment.PRODUCTION,
            deployed_at=datetime.now(),
            deployed_by=UserIdentifier(
                user_email="test@test.com",
                user_id="123",
            ),
        )
        document = TaskDeploymentDocument.from_resource("bla", deployment)

        converted = document.to_resource()
        assert converted.properties.task_variant_id == "123"
