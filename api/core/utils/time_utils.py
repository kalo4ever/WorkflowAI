import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _parse_time_and_tz_from_time_str(
    time_str: str,
    formats: tuple[str, ...] = (
        "%H:%M:%S",
        "%H:%M",
        "%H:%M:%S%z",
        "%H:%M%z",
    ),
) -> tuple[datetime, timedelta]:
    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt, dt.utcoffset() or timedelta(0)
        except ValueError:
            continue
    raise ValueError(f"Time data '{time_str}' does not match any format")


def are_time_str_equal(t1_str: str, t2_str: str) -> bool:
    try:
        t1, tz1 = _parse_time_and_tz_from_time_str(t1_str)
    except ValueError:
        logger.warning(
            "Failed to parse time string",
            extra={"time_str": t1_str},
        )
        return False

    try:
        t2, tz2 = _parse_time_and_tz_from_time_str(t2_str)
    except ValueError:
        logger.warning(
            "Failed to parse time string",
            extra={"time_str": t2_str},
        )
        return False

    if tz1 != tz2:
        return False

    return t1.time() == t2.time()
