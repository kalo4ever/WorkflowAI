import inspect
from typing import Any, Callable, Protocol, TypeVar

T = TypeVar("T", bound=Callable[..., Any])


def copy_signature(base: T) -> Callable[[Callable[..., Any]], T]:
    def decorator(fn: Callable[..., Any]) -> T:
        fn.__signature__ = inspect.signature(base)  # type: ignore
        return fn  # type: ignore

    return decorator


IncEx = set[int] | set[str] | dict[int, "IncEx"] | dict[str, "IncEx"] | None


class LogFn(Protocol):
    def __call__(self, msg: str, extra: dict[str, Any] | None = None) -> None: ...
