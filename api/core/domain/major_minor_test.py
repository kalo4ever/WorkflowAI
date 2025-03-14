import pytest

from core.domain.major_minor import MajorMinor


class TestMajorMinor:
    @pytest.mark.parametrize(
        "value, expected",
        [("1.0", MajorMinor(major=1, minor=0)), ("1.1", MajorMinor(major=1, minor=1))],
    )
    def test_from_string(self, value: str, expected: MajorMinor):
        assert MajorMinor.from_string(value) == expected

    @pytest.mark.parametrize("value", ["1.0.0", "1.0.1", "1.1.0", "1.1.1", "vla.bla", "1"])
    def test_from_string_invalid(self, value: str):
        assert MajorMinor.from_string(value) is None
