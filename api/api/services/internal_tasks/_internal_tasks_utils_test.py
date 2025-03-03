import pytest

from api.services.internal_tasks._internal_tasks_utils import internal_tools_description
from core.tools import ToolKind


def test_internal_tools_description_none() -> None:
    # Include is None, return should be empty
    result: str = internal_tools_description()
    assert result == ""


def test_internal_tools_description_empty_set() -> None:
    # Include is an empty set, return should be empty
    result: str = internal_tools_description(include=set())
    assert result == ""


def test_internal_tools_description_2_tools() -> None:
    # 2 tools included, only those 2 should be in the result
    result: str = internal_tools_description(include={ToolKind.WEB_SEARCH_GOOGLE, ToolKind.WEB_BROWSER_TEXT})
    assert ToolKind.WEB_SEARCH_GOOGLE.value in result
    assert ToolKind.WEB_BROWSER_TEXT.value in result
    assert ToolKind.WEB_SEARCH_PERPLEXITY_SONAR.value not in result


def test_internal_tools_description_all() -> None:
    # All tools included, all should be in the result
    result: str = internal_tools_description(all=True)
    for tk in ToolKind:
        assert tk.value in result


def test_internal_tools_description_all_with_include_raises() -> None:
    # Invalid parameters, should raise
    with pytest.raises(ValueError):
        internal_tools_description(all=True, include={ToolKind.WEB_SEARCH_GOOGLE})
