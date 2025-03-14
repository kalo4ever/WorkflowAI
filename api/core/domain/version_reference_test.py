from typing import Any

import pytest
from pydantic import ValidationError

from .version_reference import VersionReference


@pytest.mark.parametrize(
    "raw",
    [
        {"version": "dev", "properties": {"hello": "world"}},
    ],
)
def test_validation_error(raw: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        VersionReference.model_validate(raw)


@pytest.mark.parametrize(
    "raw",
    [
        {"version": "dev"},
        {"version": "staging"},
        {"version": "production"},
        {"version": 1},
        {"properties": {"hello": "world"}},
    ],
)
def test_validation(raw: dict[str, Any]) -> None:
    VersionReference.model_validate(raw)
