from typing import Any

import pytest
from pydantic import ValidationError

from core.domain.task_group_update import TaskGroupUpdate


# Valid test cases
@pytest.mark.parametrize(
    "update_data, expected_values",
    [
        ({"is_favorite": True}, {"is_favorite": True}),
        ({"notes": "This is a note."}, {"notes": "This is a note."}),
        ({"notes": ""}, {"notes": ""}),  # Allowing empty string for notes
    ],
)
def test_task_group_update_valid(update_data: dict[str, Any], expected_values: dict[str, Any]) -> None:
    update = TaskGroupUpdate(**update_data)
    for key, value in expected_values.items():
        assert getattr(update, key) == value


# Invalid test cases
@pytest.mark.parametrize(
    "update_data, expected_error",
    [
        ({"add_alias": "new_alias"}, "Updating a group alias is deprecated "),
        ({"remove_alias": "old_alias"}, "Updating a group alias is deprecated "),
        ({}, "At least one of is_favorite, or notes must be set"),
        ({"is_favorite": "yes"}, "Input should be a valid boolean"),
        ({"notes": "   "}, "Notes cannot be whitespace-only strings"),
    ],
)
def test_task_group_update_invalid(update_data: dict[str, Any], expected_error: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        TaskGroupUpdate(**update_data)
    assert expected_error in str(exc_info.value)
