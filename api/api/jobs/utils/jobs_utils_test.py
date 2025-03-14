from unittest.mock import Mock, patch

import pytest

from api.jobs.utils.jobs_utils import get_task_run_str, get_task_str_for_slack, get_task_url
from core.domain.analytics_events.analytics_events import OrganizationProperties
from core.domain.events import Event


@pytest.fixture
def event() -> Event:
    return Event(
        organization_properties=OrganizationProperties(organization_slug="test-org", tenant="test-org-id"),
    )


class TestGetTaskUrl:
    def test_returns_none_when_no_organization_slug(self) -> None:
        event = Event(organization_properties=None)

        result = get_task_url(event=event, task_id="123", task_schema_id=456)

        assert result is None

    @patch.dict("os.environ", {"WORKFLOWAI_APP_URL": "https://app.workflow.ai"})
    def test_returns_correct_url(self, event: Event) -> None:
        result = get_task_url(event=event, task_id="test-task-id", task_schema_id=456)

        assert result == "https://app.workflow.ai/test-org/agents/test-task-id/456"


class TestGetTaskStrForSlack:
    @patch("api.jobs.utils.jobs_utils.get_task_url", return_value=None)
    def test_returns_task_id_when_no_url(self, mock_get_task_url: Mock, event: Event) -> None:
        result = get_task_str_for_slack(event=event, task_id="test-task-id", task_schema_id=456)

        assert result == "test-task-id"
        mock_get_task_url.assert_called_once_with(event=event, task_id="test-task-id", task_schema_id=456)

    @patch("api.jobs.utils.jobs_utils.get_task_url")
    def test_returns_hyperlink_when_url_exists(self, mock_get_task_url: Mock, event: Event) -> None:
        mock_get_task_url.return_value = "https://app.workflow.ai/test-org/agents/123/456"

        result = get_task_str_for_slack(event=event, task_id="123", task_schema_id=456)

        assert result == "<https://app.workflow.ai/test-org/agents/123/456|123>"
        mock_get_task_url.assert_called_once_with(event=event, task_id="123", task_schema_id=456)


class TestGetTaskRunStr:
    @patch("api.jobs.utils.jobs_utils.get_task_url", return_value=None)
    def test_returns_basic_str_when_no_url(self, mock_get_task_url: Mock, event: Event) -> None:
        result = get_task_run_str(
            event=event,
            task_id="test-task-id",
            task_schema_id=456,
            task_run_id="test-run-id",
        )

        assert result == "task run id:test-run-id"
        mock_get_task_url.assert_called_once_with(
            event=event,
            task_id="test-task-id",
            task_schema_id=456,
        )

    @patch("api.jobs.utils.jobs_utils.get_task_url")
    def test_returns_url_with_run_id_when_url_exists(self, mock_get_task_url: Mock, event: Event) -> None:
        mock_get_task_url.return_value = "https://app.workflow.ai/test-org/agents/123/456"

        result = get_task_run_str(
            event=event,
            task_id="123",
            task_schema_id=456,
            task_run_id="test-run-id",
        )

        assert result == "https://app.workflow.ai/test-org/agents/123/456/runs?taskRunId=test-run-id"
        mock_get_task_url.assert_called_once_with(
            event=event,
            task_id="123",
            task_schema_id=456,
        )
