from datetime import date
from unittest.mock import Mock, patch

import pytest

from api.services.uptime_service import UptimeService


# Test subclass that exposes the protected method for testing
class TestableUptimeService(UptimeService):
    def check_date_diff(self, from_date: date, to_date: date, tolerance: int, service_name: str) -> None:
        return self._check_date_diff(from_date, to_date, tolerance, service_name)


class TestUptimeService:
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
