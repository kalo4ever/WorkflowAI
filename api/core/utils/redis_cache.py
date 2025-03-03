import asyncio
import functools
import hashlib
import logging
import os
import pickle
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_logger = logging.getLogger(__name__)


def get_redis_client() -> Any:
    import redis.asyncio as aioredis

    try:
        async_cache: aioredis.Redis | None = aioredis.from_url(os.environ["JOBS_BROKER_URL"])  # pyright: ignore
    except (KeyError, ValueError):
        async_cache = None

    return async_cache


def redis_cached(expiration_seconds: int = 60 * 60 * 24) -> Callable[[F], F]:  # default ttl is 1 day
    async_cache = get_redis_client()
    if not async_cache:
        _logger.warning("Redis cache is not available, skipping decorator")

        def decorator(func: F) -> F:
            return func

        return decorator

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                args_bytes: bytes = pickle.dumps((args, kwargs))
                args_hash: str = hashlib.sha256(args_bytes).hexdigest()
                module_name: str = func.__module__
                func_name: str = func.__name__
                cache_key: str = f"{module_name}.{func_name}:{args_hash}"

                cached_result: Optional[bytes] = await async_cache.get(cache_key)  # pyright: ignore
                if cached_result:
                    return pickle.loads(cached_result)  # pyright: ignore

                result: Any = (
                    await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                )
                await async_cache.setex(cache_key, expiration_seconds, pickle.dumps(result))  # pyright: ignore
                return result
            except Exception:
                return await func(*args, **kwargs)

        return async_wrapper  # type: ignore

    return decorator
