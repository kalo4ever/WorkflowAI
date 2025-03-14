import asyncio

import pytest

from core.domain.tool_call import ToolCall
from core.runners.workflowai.tool_cache import ToolCache


@pytest.fixture
def tool_cache() -> ToolCache:
    return ToolCache()


async def test_tool_cache_basic_operations(tool_cache: ToolCache):
    # Test set and get
    await tool_cache.set("test_tool", {"arg1": "value1"}, "result1")
    result = await tool_cache.get("test_tool", {"arg1": "value1"})
    assert isinstance(result, ToolCall)
    assert result.tool_name == "test_tool"
    assert result.tool_input_dict == {"arg1": "value1"}
    assert result.result == "result1"

    # Test get with non-existent key
    result = await tool_cache.get("non_existent", {"arg1": "value1"})
    assert result is None

    # Test values
    values = list(await tool_cache.values())
    assert len(values) == 1
    assert isinstance(values[0], ToolCall)
    assert values[0].tool_name == "test_tool"


async def test_tool_cache_argument_sensitivity(tool_cache: ToolCache):
    # Test that different argument orders produce the same result
    await tool_cache.set("test_tool", {"a": 1, "b": 2}, "result")
    await tool_cache.set("test_tool", {"b": 2, "a": 1}, "result")

    values = list(await tool_cache.values())
    assert len(values) == 1  # Should only store one value as args are equivalent


async def test_tool_cache_concurrent_operations(tool_cache: ToolCache):
    async def writer(i: int):
        await tool_cache.set(f"tool_{i}", {"arg": i}, f"result_{i}")

    async def reader(i: int) -> ToolCall | None:
        return await tool_cache.get(f"tool_{i}", {"arg": i})

    # Create concurrent write operations
    write_tasks = [writer(i) for i in range(10)]
    await asyncio.gather(*write_tasks)

    # Create concurrent read operations
    read_tasks = [reader(i) for i in range(10)]
    results = await asyncio.gather(*read_tasks)

    # Verify results
    for i, result in enumerate(results):
        assert result is not None
        assert result.tool_name == f"tool_{i}"
        assert result.tool_input_dict == {"arg": i}
        assert result.result == f"result_{i}"

    # Verify final cache state
    values = list(await tool_cache.values())
    assert len(values) == 10


async def test_tool_cache_concurrent_read_write(tool_cache: ToolCache):
    async def concurrent_operation(i: int):
        # Write operation
        await tool_cache.set(f"tool_{i}", {"arg": i}, f"result_{i}")
        # Immediate read operation
        result = await tool_cache.get(f"tool_{i}", {"arg": i})
        assert result is not None
        assert result.tool_name == f"tool_{i}"
        assert result.tool_input_dict == {"arg": i}
        assert result.result == f"result_{i}"

    # Create multiple concurrent read-write operations
    tasks = [concurrent_operation(i) for i in range(5)]
    await asyncio.gather(*tasks)

    # Verify final state
    values = list(await tool_cache.values())
    assert len(values) == 5
