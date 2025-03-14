import asyncio

from .aio import parallel


async def test_parallel() -> None:
    async def add(x: int, y: int) -> int:
        await asyncio.sleep(0.1)  # Simulate async I/O, e.g. a request
        return x + y

    expected_results = [3, 7, 11]

    results = [i async for i in parallel(add, [(1, 2), (3, 4), (5, 6)])]
    results.sort()
    assert results == expected_results


async def test_parallel_limit() -> None:
    counter = 0
    max_counter = 0

    async def mock_func(_val: int):
        nonlocal counter, max_counter
        counter += 1
        max_counter = max(max_counter, counter)
        await asyncio.sleep(0.1)
        counter -= 1

    args_list = [(i,) for i in range(10)]
    limit = 2

    async for _ in parallel(mock_func, args_list, limit):
        pass

    assert max_counter == limit
