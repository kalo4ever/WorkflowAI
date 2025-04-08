from typing import Any
from unittest.mock import Mock

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from api.routers.runs_v1 import SearchTaskRunsRequest
from api.services.version_test import mock_aiter
from core.domain.task_info import TaskInfo
from core.domain.task_run import Run
from core.domain.task_run_query import SerializableTaskRunQuery
from core.utils.uuid import uuid7
from tests.models import task_run_ser


class TestSearchTaskRunsRequestQuery:
    @pytest.mark.parametrize("field_name", ["metadata.key", "metadata.key.subkey"])
    def test_valid_field_name(self, field_name: str):
        request = SearchTaskRunsRequest.Query.model_validate(
            {"field_name": field_name, "operator": "is", "values": ["value"]},
        )
        assert request.field_name == field_name

    @pytest.mark.parametrize("field_name", [1, "[invalid]", "INSERT?", "INSERT INTO ", None])
    def test_invalid_field_name(self, field_name: Any):
        with pytest.raises(ValidationError):
            SearchTaskRunsRequest.Query.model_validate(
                {"field_name": field_name, "operator": "is", "values": ["value"]},
            )


class TestLatestRun:
    # Making sure the mock happens after the test_api_client is created
    @pytest.fixture(autouse=True)
    def returned_run(self, test_api_client: AsyncClient, mock_storage: Mock):
        run = task_run_ser(id=str(uuid7()), task_uid=1, task_schema_id=1, status="success")
        mock_storage.task_runs.fetch_task_run_resources.return_value = mock_aiter(run)
        mock_storage.tasks.get_task_info.return_value = TaskInfo(task_id="bla", uid=2)
        return run

    async def test_latest_run(
        self,
        test_api_client: AsyncClient,
        mock_storage: Mock,
        returned_run: Run,
    ):
        response = await test_api_client.get("/v1/_/agents/bla/runs/latest")
        assert response.status_code == 200
        assert response.json()["id"] == returned_run.id

        mock_storage.task_runs.fetch_task_run_resources.assert_called_once_with(
            task_uid=2,
            query=SerializableTaskRunQuery(
                task_id="bla",
                exclude_fields={"llm_completions"},
                limit=1,
            ),
        )

    async def test_latest_run_with_status(
        self,
        test_api_client: AsyncClient,
        returned_run: Run,
        mock_storage: Mock,
    ):
        response = await test_api_client.get("/v1/_/agents/bla/runs/latest?is_success=true")
        assert response.status_code == 200
        assert response.json()["id"] == returned_run.id

        mock_storage.task_runs.fetch_task_run_resources.assert_called_once_with(
            task_uid=2,
            query=SerializableTaskRunQuery(
                task_id="bla",
                exclude_fields={"llm_completions"},
                limit=1,
                status={"success"},
            ),
        )

    async def test_latest_with_schema_id(
        self,
        test_api_client: AsyncClient,
        returned_run: Run,
        mock_storage: Mock,
    ):
        response = await test_api_client.get("/v1/_/agents/bla/runs/latest?schema_id=1")
        assert response.status_code == 200
        assert response.json()["id"] == returned_run.id

        mock_storage.task_runs.fetch_task_run_resources.assert_called_once_with(
            task_uid=2,
            query=SerializableTaskRunQuery(
                task_id="bla",
                task_schema_id=1,
                exclude_fields={"llm_completions"},
                limit=1,
            ),
        )
