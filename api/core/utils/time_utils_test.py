from datetime import datetime, timedelta, timezone

import pytest

from core.utils.time_utils import (
    _parse_time_and_tz_from_time_str,  # pyright: ignore [reportPrivateUsage]
    are_time_str_equal,
)


@pytest.mark.parametrize(
    "time_str1, time_str2",
    [
        ("12:00:00", "12:00"),
        ("12:00:00", "12:00:00"),
        ("22:00:00", "22:00:00"),
        ("22:00:00", "22:00"),
        ("12:00:00+0000", "12:00"),
        ("12:00+0000", "12:00"),
    ],
)
def test_parse_time_equal(time_str1: str, time_str2: str):
    assert are_time_str_equal(time_str1, time_str2) is True


@pytest.mark.parametrize(
    "time_str1, time_str2",
    [
        ("12:00:00", "12:01"),
        ("12:00:00", "12:00:01"),
        ("22:00:00", "22:01:00"),
        ("12:00:00+01:00", "12:00"),
        ("12:00+00:00", "12:00+01:00"),
        ("12:00:00+01:00", "11:00:00Z"),
        ("unparsable", "12:00"),
        ("12:00", "unparsable"),
    ],
)
def test_parse_time_not_equal(time_str1: str, time_str2: str):
    assert are_time_str_equal(time_str1, time_str2) is False


@pytest.mark.parametrize(
    "time_str, expected_datetime, expected_tz",
    [
        ("12:00:00", datetime(1900, 1, 1, 12, 0), timedelta(0)),
        ("12:00", datetime(1900, 1, 1, 12, 0), timedelta(0)),
        ("12:00:00+0000", datetime(1900, 1, 1, 12, 0, tzinfo=timezone.utc), timedelta(0)),
        ("12:00+0000", datetime(1900, 1, 1, 12, 0, tzinfo=timezone.utc), timedelta(0)),
    ],
)
def test_parse_datetime_from_time_str(time_str: str, expected_datetime: datetime, expected_tz: timedelta):
    dt, tz = _parse_time_and_tz_from_time_str(time_str)
    assert dt == expected_datetime
    assert tz == expected_tz


@pytest.mark.parametrize(
    "invalid_time_str",
    [
        "25:00:00",  # Invalid hour
        "12:60:00",  # Invalid minute
        "12:00:60",  # Invalid second
        "12:00:00+2500",  # Invalid timezone
    ],
)
def test_parse_datetime_from_time_str_invalid(invalid_time_str: str):
    with pytest.raises(ValueError):
        _parse_time_and_tz_from_time_str(invalid_time_str)
