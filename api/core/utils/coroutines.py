import asyncio
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


def safe_in_background(
    corot: Coroutine[Any, Any, _T],
    container: set[asyncio.Task[_T | None]],
) -> asyncio.Task[Any]:
    """Adds a coroutine to a set for safe background execution
    All errors are captured in sentry"""
    t = asyncio.create_task(sentry_wrap(corot))
    container.add(t)
    t.add_done_callback(container.remove)
    return t


def safe_task_group_add(tg: asyncio.TaskGroup, corot: Coroutine[Any, Any, Any]):
    tg.create_task(sentry_wrap(corot))


@contextmanager
def capture_errors(logger: logging.Logger, msg: str):
    try:
        yield
    except Exception:
        logger.exception(msg)
