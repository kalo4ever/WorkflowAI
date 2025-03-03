from typing import Any
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from sentry_sdk import Scope

from api.errors import configure_scope_for_error
from core.domain.errors import ScopeConfigurableError


class _ScopeConfigurableError(ScopeConfigurableError):
    def configure_scope(self, scope: Scope) -> None:
        scope.set_tag("error_type", "test_error")
        scope.set_extra("error_detail", "test_detail")


class TestConfigureScopeForError:
    @pytest.fixture
    def mock_scope(self):
        mock_scope = Mock()
        mock_scope.__enter__ = MagicMock(return_value=mock_scope)
        mock_scope.__exit__ = MagicMock()
        with patch("api.errors.new_scope", autospec=True, return_value=mock_scope):
            yield mock_scope

    def test_configure_scope_for_error_with_tags(self, mock_scope: Mock):
        tags: dict[str, Any] = {"tag1": "value1", "tag2": True, "tag3": 42}

        with configure_scope_for_error(Exception(), tags=tags):
            pass

        mock_scope.set_extra.assert_not_called()

        assert mock_scope.set_tag.call_count == 3
        mock_scope.set_tag.assert_has_calls(
            [
                call("tag1", "value1"),
                call("tag2", True),
                call("tag3", 42),
            ],
        )

    def test_configure_scope_for_error_with_extras(self, mock_scope: Mock):
        extras: dict[str, Any] = {"extra1": "value1", "extra2": {"nested": "value"}}

        with configure_scope_for_error(Exception(), extras=extras):
            pass

        mock_scope.set_tag.assert_not_called()
        assert mock_scope.set_extra.call_count == 2
        mock_scope.set_extra.assert_has_calls(
            [
                call("extra1", "value1"),
                call("extra2", {"nested": "value"}),
            ],
        )

    def test_configure_scope_for_error_with_scope_configurable_error(self, mock_scope: Mock):
        error = _ScopeConfigurableError()

        with configure_scope_for_error(error):
            pass

        mock_scope.set_tag.assert_called_with("error_type", "test_error")
        mock_scope.set_extra.assert_called_with("error_detail", "test_detail")
