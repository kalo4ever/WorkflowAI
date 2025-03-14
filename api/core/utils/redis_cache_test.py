import asyncio
import pickle
from unittest.mock import AsyncMock, Mock, patch

import pytest

from core.utils.redis_cache import redis_cached


async def test_redis_cached_hit() -> None:
    # Setup mock cache with existing data
    mock_cache = AsyncMock()
    cached_result = "cached_value"
    mock_cache.get.return_value = pickle.dumps(cached_result)

    mock_inner = AsyncMock(return_value="fresh_value")

    with patch("core.utils.redis_cache.get_redis_client", return_value=mock_cache):

        @redis_cached()
        async def test_func(param: str) -> str:
            return await mock_inner(param)

        result = await test_func("test_param")

    assert result == "cached_value"
    mock_cache.get.assert_called_once()
    mock_cache.setex.assert_not_called()
    mock_inner.assert_not_called()  # Function should not be called on cache hit


async def test_redis_cached_miss() -> None:
    # Setup mock cache with no existing data
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    mock_inner = AsyncMock(return_value="fresh_value")

    @redis_cached(expiration_seconds=300)
    async def test_func(param: str) -> str:
        return await mock_inner(param)

    with patch("core.utils.redis_cache.get_redis_client", return_value=mock_cache):

        @redis_cached()
        async def test_func(param: str) -> str:
            return await mock_inner(param)

        result = await test_func("test_param")

    assert result == "fresh_value"
    mock_cache.get.assert_called_once()
    mock_cache.setex.assert_called_once()
    mock_inner.assert_called_once_with("test_param")  # Function should be called on cache miss


async def test_redis_cached_non_async_function() -> None:
    """
    This test verifies that redis_cached() works with non-async functions.
    The decorator wraps non-async functions to make them awaitable since it needs to
    interact with Redis asynchronously, even though the wrapped function is synchronous.
    """

    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    mock_inner = Mock(return_value="sync_value")

    with patch("core.utils.redis_cache.get_redis_client", return_value=mock_cache):

        @redis_cached()
        def test_func(param: str) -> str:  # Note: non-async function
            return mock_inner(param)

        # We await because redis_cached() makes the function awaitable to handle Redis I/O
        result = await test_func("test_param")  # pyright: ignore

    assert result == "sync_value"
    mock_cache.setex.assert_called_once()
    mock_inner.assert_called_once_with("test_param")  # Function should be called


async def test_redis_cached_cache_error() -> None:
    mock_cache = AsyncMock()
    mock_cache.get.side_effect = Exception("Redis connection error")

    mock_inner = AsyncMock(return_value="fallback_value")

    with patch("core.utils.redis_cache.get_redis_client", return_value=mock_cache):

        @redis_cached()
        def test_func(param: str) -> str:  # Note: non-async function
            return mock_inner(param)

        # We await because redis_cached() makes the function awaitable to handle Redis I/O
        result = await test_func("test_param")  # pyright: ignore

    assert result == "fallback_value"
    mock_cache.get.assert_called_once()
    mock_cache.setex.assert_not_called()
    mock_inner.assert_called_once_with("test_param")  # Function should be called on error


async def test_redis_cached_with_complex_args() -> None:
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    mock_inner = AsyncMock(return_value={"result": 30})

    with patch("core.utils.redis_cache.get_redis_client", return_value=mock_cache):

        @redis_cached()
        async def test_func(a: int, b: dict[str, int], c: str = "default") -> dict[str, int]:
            return await mock_inner(a, b, c)

        complex_args = {"value": 20}
        result = await test_func(10, complex_args, c="custom")

    assert result == {"result": 30}
    mock_cache.get.assert_called_once()
    mock_cache.setex.assert_called_once()
    mock_inner.assert_called_once_with(10, complex_args, "custom")  # Function should be called with correct args


@pytest.mark.skip(reason="This test requires a real Redis instance")
async def test_redis_cached_expiration_real() -> None:
    """
    Test cache expiration using the real Redis instance.
    We only track function calls to verify cache behavior.
    """
    call_count: int = 0

    @redis_cached(expiration_seconds=1)
    async def test_func(param: str) -> str:
        nonlocal call_count
        call_count += 1
        return f"fresh_value_{call_count}"

    # First call: cache miss; function should be called
    result1: str = await test_func("test_param")
    assert result1 == "fresh_value_1"
    first_call_count: int = call_count

    # Second call immediately: cache hit; function should not be called again
    result2: str = await test_func("test_param")
    assert result2 == "fresh_value_1"
    assert call_count == first_call_count  # Should not have increased

    # Wait for the cache to expire
    await asyncio.sleep(2)

    # Third call after expiration: cache miss; function should be called again
    result3: str = await test_func("test_param")
    assert result3 == "fresh_value_2"
    assert call_count == first_call_count + 1  # Should have increased by 1
