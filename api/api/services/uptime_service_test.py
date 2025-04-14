import json
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Generator, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
from pytest_httpx import HTTPXMock

from api.services.uptime_service import UptimeService
from core.agents.uptime_extraction_agent import UptimeExtractorAgentInput, UptimeExtractorAgentOutput


class TestUptimeService:
    @pytest.fixture
    def uptime_service(self) -> UptimeService:
        return UptimeService()

    @pytest.fixture
    def logger_mock(self) -> MagicMock:
        return MagicMock(spec=logging.Logger)

    @pytest.fixture
    def uptime_service_with_mock_logger(self, logger_mock: MagicMock) -> UptimeService:
        return UptimeService(logger=logger_mock)

    @pytest.fixture
    def mock_browser_text(self) -> Generator[AsyncMock, None, None]:
        with patch("api.services.uptime_service.browser_text") as mock:
            mock.return_value = "<html>Test content</html>"
            yield mock

    @pytest.fixture
    def mock_uptime_agent(self) -> Generator[AsyncMock, None, None]:
        with patch("api.services.uptime_service.uptime_extraction_agent", new_callable=AsyncMock) as mock:
            yield mock

    @pytest.fixture
    def openai_status_fixture(self) -> dict[str, Any]:
        fixture_path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "uptime" / "openai_status.json"
        with open(fixture_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def openai_status_components_fixture(self) -> dict[str, Any]:
        fixture_path = (
            Path(__file__).parent.parent.parent / "tests" / "fixtures" / "uptime" / "openai_status_components.json"
        )
        with open(fixture_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def status_data(self, request: pytest.FixtureRequest, openai_status_fixture: dict[str, Any]) -> dict[str, Any]:
        if request.param == "openai_status_fixture":
            return openai_status_fixture
        return {}

    @pytest.fixture
    def component_data(
        self,
        request: pytest.FixtureRequest,
        openai_status_components_fixture: dict[str, Any],
    ) -> dict[str, Any]:
        if request.param == "openai_status_components_fixture":
            return openai_status_components_fixture
        return {}

    def test_init_with_logger(self, logger_mock: MagicMock) -> None:
        service = UptimeService(logger=logger_mock)
        # Using __dict__ to access protected attribute for testing
        assert service.__dict__["_logger"] is logger_mock

    def test_init_without_logger(self) -> None:
        service = UptimeService()
        # Using __dict__ to access protected attribute for testing
        assert isinstance(service.__dict__["_logger"], logging.Logger)
        assert service.__dict__["_logger"].name == "api.services.uptime_service"

    @pytest.mark.parametrize(
        "uptime_value, since_value, expected_result, expected_since",
        [
            (0.995, "2025-01-01", 0.995, date(2025, 1, 1)),
            (None, None, None, None),
        ],
    )
    async def test_run_uptime_extraction_success(
        self,
        mock_uptime_agent: AsyncMock,
        mock_browser_text: AsyncMock,
        uptime_value: Optional[float],
        since_value: Optional[date],
        expected_result: float,
        expected_since: date,
        uptime_service: UptimeService,
    ) -> None:
        # Arrange
        status_page_url = "https://test-status.com"
        extraction_instructions = "Test instructions"
        page_content = "<html>Test content</html>"

        mock_browser_text.return_value = page_content
        mock_uptime_agent.return_value = MagicMock(
            output=UptimeExtractorAgentOutput(uptime=uptime_value, since=since_value),
        )

        # Act
        result = await uptime_service._get_uptime_info(  # type: ignore[reportPrivateUsage]
            status_page_url=status_page_url,
            extraction_instructions=extraction_instructions,
        )

        # Assert
        assert result == (expected_result, expected_since)
        mock_browser_text.assert_called_once_with(status_page_url)
        mock_uptime_agent.assert_called_once()
        agent_input = mock_uptime_agent.call_args[0][0]
        assert isinstance(agent_input, UptimeExtractorAgentInput)
        assert agent_input.status_page_content == page_content
        assert agent_input.extraction_instructions == extraction_instructions

    async def test_run_uptime_extraction_unparsable_date(
        self,
        mock_uptime_agent: AsyncMock,
        mock_browser_text: AsyncMock,
        uptime_service_with_mock_logger: UptimeService,
        logger_mock: MagicMock,
    ) -> None:
        # Arrange
        status_page_url = "https://test-status.com"
        extraction_instructions = "Test instructions"
        page_content = "<html>Test content</html>"
        expected_uptime = 0.99

        mock_browser_text.return_value = page_content
        mock_uptime_agent.return_value = MagicMock(
            output=UptimeExtractorAgentOutput(uptime=expected_uptime, since="not-a-valid-date"),
        )

        # Act
        result = await uptime_service_with_mock_logger._get_uptime_info(  # type: ignore[reportPrivateUsage]
            status_page_url=status_page_url,
            extraction_instructions=extraction_instructions,
        )

        # Assert
        assert result == (expected_uptime, None)
        mock_browser_text.assert_called_once_with(status_page_url)
        mock_uptime_agent.assert_called_once()
        logger_mock.error.assert_called_once()
        assert "Invalid since date" in logger_mock.error.call_args[0][0]

    async def test_run_uptime_extraction_browser_exception(
        self,
        mock_browser_text: AsyncMock,
        uptime_service_with_mock_logger: UptimeService,
        logger_mock: MagicMock,
    ) -> None:
        # Arrange
        status_page_url = "https://test-status.com"
        mock_browser_text.side_effect = Exception("Browser error")

        # Act
        result = await uptime_service_with_mock_logger._get_uptime_info(  # type: ignore[reportPrivateUsage]
            status_page_url=status_page_url,
            extraction_instructions=None,
        )

        # Assert
        assert result == (None, None)
        logger_mock.exception.assert_called_once()
        assert "Error extracting uptime for" in logger_mock.exception.call_args[0][0]

    @pytest.mark.parametrize(
        "status_data, expected_component_id",
        [
            ("openai_status_fixture", "01JMXBRMFE6N2NNT7DG6XZQ6PW"),
        ],
        indirect=["status_data"],
    )
    async def test_get_chat_component_id(
        self,
        status_data: dict[str, Any],
        expected_component_id: str,
        uptime_service: UptimeService,
        httpx_mock: HTTPXMock,
    ) -> None:
        # Arrange
        httpx_mock.add_response(
            url="https://status.openai.com/proxy/status.openai.com",
            json=status_data,
            status_code=200,
        )

        # Act
        result = await uptime_service._get_openai_chat_api_component_id()  # type: ignore[reportPrivateUsage]

        # Assert
        assert result == expected_component_id
        assert len(httpx_mock.get_requests()) == 1
        request = httpx_mock.get_requests()[0]
        assert request.url == "https://status.openai.com/proxy/status.openai.com"

    async def test_get_chat_component_id_error(
        self,
        uptime_service_with_mock_logger: UptimeService,
        logger_mock: MagicMock,
        httpx_mock: HTTPXMock,
    ) -> None:
        # Arrange
        httpx_mock.add_exception(httpx.ConnectError("Failed to connect"))

        # Act
        result = await uptime_service_with_mock_logger._get_openai_chat_api_component_id()  # type: ignore[reportPrivateUsage]

        # Assert
        assert result is None
        logger_mock.exception.assert_called_once()
        assert "Error finding Chat API component ID" in logger_mock.exception.call_args[0][0]

    @pytest.mark.parametrize(
        "component_data, component_id, expected_uptime, expected_date",
        [
            ("openai_status_components_fixture", "01JMXBRMFE6N2NNT7DG6XZQ6PW", "99.92", True),
            ("openai_status_components_fixture", "non_existent_id", None, False),
        ],
        indirect=["component_data"],
    )
    async def test_get_open_ai_component_uptime(
        self,
        component_data: dict[str, Any],
        component_id: str,
        expected_uptime: Optional[str],
        expected_date: bool,
        uptime_service: UptimeService,
        httpx_mock: HTTPXMock,
    ) -> None:
        # Arrange
        test_date = date(2025, 4, 10)
        expected_start_date = test_date - timedelta(days=90)

        # Create the exact URL we expect
        expected_start_at = f"{expected_start_date.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        expected_end_at = f"{test_date.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        url_base = "https://status.openai.com/proxy/status.openai.com/component_impacts"
        url = f"{url_base}?start_at={expected_start_at}&end_at={expected_end_at}"

        # Configure mock response
        httpx_mock.add_response(
            url=url,
            json=component_data,
            status_code=200,
        )

        # Act
        uptime, since = await uptime_service._get_open_ai_component_uptime(  # type: ignore[reportPrivateUsage]
            current_date=test_date,
            component_id=component_id,
        )

        # Assert
        assert uptime == expected_uptime
        if expected_date:
            assert since == expected_start_date
        else:
            assert since is None

        # Verify request was made
        requests = httpx_mock.get_requests()
        assert len(requests) == 1

        # Convert URL to string for comparison
        request_url = str(requests[0].url)
        assert url_base in request_url
        assert f"start_at={expected_start_at}" in request_url
        assert f"end_at={expected_end_at}" in request_url

    async def test_get_open_ai_component_uptime_exception(
        self,
        uptime_service_with_mock_logger: UptimeService,
        logger_mock: MagicMock,
        httpx_mock: HTTPXMock,
    ) -> None:
        # Arrange
        test_date = date(2025, 4, 10)
        component_id = "some_component_id"

        # Create expected URL
        expected_start_date = test_date - timedelta(days=90)
        expected_start_at = f"{expected_start_date.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        expected_end_at = f"{test_date.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        url_base = "https://status.openai.com/proxy/status.openai.com/component_impacts"
        url = f"{url_base}?start_at={expected_start_at}&end_at={expected_end_at}"

        # Add exception for this specific URL
        httpx_mock.add_exception(httpx.ConnectError("Failed to connect"), url=url)

        # Act
        uptime, since = await uptime_service_with_mock_logger._get_open_ai_component_uptime(  # type: ignore[reportPrivateUsage]
            current_date=test_date,
            component_id=component_id,
        )

        # Assert
        assert uptime is None
        assert since is None
        logger_mock.exception.assert_called_once()
        assert "Error getting OpenAI component uptime" in logger_mock.exception.call_args[0][0]

    @pytest.mark.parametrize(
        "from_date,to_date,tolerance,service_name,should_log",
        [
            # Date difference is greater than tolerance - should log warning
            (date(2023, 5, 15), date(2023, 5, 10), 3, "workflowai", True),
            # Date difference is equal to tolerance - should not log warning
            (date(2023, 5, 15), date(2023, 5, 12), 3, "openai", False),
            # Date difference is less than tolerance - should not log warning
            (date(2023, 5, 15), date(2023, 5, 13), 3, "workflowai", False),
            # Edge case: same dates - should not log warning
            (date(2023, 5, 15), date(2023, 5, 15), 0, "openai", False),
            # Edge case: negative tolerance - should log warning if any difference
            (date(2023, 5, 15), date(2023, 5, 14), -1, "workflowai", True),
        ],
    )
    def test_check_date_diff(
        self,
        from_date: date,
        to_date: date,
        tolerance: int,
        service_name: str,
        should_log: bool,
    ) -> None:
        # Arrange
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            service = TestableUptimeService()

            # Act
            service.check_date_diff(from_date, to_date, tolerance, service_name)

            # Assert
            if should_log:
                mock_logger.warning.assert_called_once_with(
                    "Uptime date difference is greater than tolerance",
                    extra={
                        "from_date": from_date,
                        "to_date": to_date,
                        "tolerance": tolerance,
                        "service_name": service_name,
                    },
                )
            else:
                mock_logger.warning.assert_not_called()


# Test subclass that exposes the protected method for testing
class TestableUptimeService(UptimeService):
    def check_date_diff(self, from_date: date, to_date: date, tolerance: int, service_name: str) -> None:
        return self._check_date_diff(from_date, to_date, tolerance, service_name)
