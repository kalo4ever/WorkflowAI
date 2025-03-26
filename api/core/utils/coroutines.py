import logging
from collections.abc import Coroutine
from contextlib import contextmanager
from typing import Any, TypeVar

from sentry_sdk import capture_exception

_T = TypeVar("_T")


def sentry_wrap(corot: Coroutine[Any, Any, _T]) -> Coroutine[Any, Any, _T | None]:
    async def captured() -> _T | None:
        try:
            return await corot
        except Exception as e:
            capture_exception(e)
            return None

    return captured()


@contextmanager
def capture_errors(logger: logging.Logger, msg: str):
    try:
        yield
    except Exception:
        logger.exception(msg)
