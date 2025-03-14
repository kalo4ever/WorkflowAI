from datetime import datetime
from unittest.mock import Mock

from httpx import AsyncClient

from api.routers.versions_v1 import MajorVersion
from core.domain.models import Model
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.version_major import VersionMajor


class TestMajorVersionFromDomain:
    def test_from_domain_model_str(self):
        """Test that we can convert a VersionMajor to a MajorVersion when the model is a non
        identified string
        """
        major = VersionMajor(
            similarity_hash="123",
            major=1,
            schema_id=1,
            properties=VersionMajor.Properties(),
            minors=[
                VersionMajor.Minor(
                    id="123",
                    iteration=1,
                    minor=1,
                    properties=VersionMajor.Minor.Properties(model="gpt-4o"),
                ),
            ],
            created_at=datetime.now(),
        )
        major_version = MajorVersion.from_domain(major)
        assert major_version.major == 1
        assert major_version.schema_id == 1
        assert major_version.minors[0].model == "gpt-4o"

    def test_from_domain_model_enum(self):
        major = VersionMajor(
            similarity_hash="123",
            major=1,
            schema_id=1,
            properties=VersionMajor.Properties(),
            minors=[
                VersionMajor.Minor(
                    id="123",
                    iteration=1,
                    minor=1,
                    properties=VersionMajor.Minor.Properties(model=Model.GPT_4O_LATEST),
                ),
            ],
            created_at=datetime.now(),
        )
        major_version = MajorVersion.from_domain(major)
        assert major_version.major == 1
        assert major_version.schema_id == 1
        assert isinstance(major_version.minors[0].model, Model)
        assert major_version.minors[0].model == Model.GPT_4O_LATEST


class TestImproveVersion:
    async def test_improve_version(self, mock_internal_tasks_service: Mock, test_api_client: AsyncClient):
        mock_internal_tasks_service.improve_prompt.run.return_value = (
            TaskGroupProperties(model="gpt-4o", instructions="This is an instructions."),
            ["Minor tweaks"],
        )
        response = await test_api_client.post(
            "/v1/test/agents/test/versions/improve",
            json={
                "run_id": "123",
                "user_evaluation": "This is a user evaluation.",
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "improved_properties": {
                "model": "gpt-4o",
                "instructions": "This is an instructions.",
                "has_templated_instructions": False,
            },
            "changelog": ["Minor tweaks"],
        }
