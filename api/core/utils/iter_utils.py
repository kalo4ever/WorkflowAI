import logging
from collections.abc import Callable, Iterable
from typing import Optional, TypeVar

from core.utils.generics import T


def first_where(iterable: Iterable[T], condition: Callable[[T], bool], default: Optional[T] = None) -> Optional[T]:
    """Return the first item in 'iterable' that satisfies 'condition' if any, else return 'default'."""

    return next((item for item in iterable if condition(item)), default)


def last_where(iterable: Iterable[T], condition: Callable[[T], bool], default: Optional[T] = None) -> Optional[T]:
    """Return the last item in 'iterable' that satisfies 'condition' if any, else return 'default'."""

    return first_where(reversed(list(iterable)), condition, default)


T2 = TypeVar("T2")


def safe_map(iterable: Iterable[T], func: Callable[[T], T2], logger: logging.Logger | None = None) -> list[T2]:
    """Map 'iterable' with 'func' and return a list of results, ignoring any errors."""

    results: list[T2] = []
    for item in iterable:
        try:
            results.append(func(item))
        except Exception as e:
            if logger:
                logger.exception(e)

    return results


def safe_map_optional(
    iterable: Iterable[T] | None,
    func: Callable[[T], T2],
    logger: logging.Logger | None = None,
) -> list[T2] | None:
    if not iterable:
        return None

    return safe_map(iterable, func, logger) or None
