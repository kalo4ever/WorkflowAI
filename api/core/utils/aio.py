import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, TypeVar

T_Ret = TypeVar("T_Ret")  # Type variable for return type

# TODO: find a way to type the fn arguments


async def parallel(
    func: Callable[..., Awaitable[T_Ret]],
    args_list: list[Any],
    limit: int = 20,
) -> AsyncGenerator[T_Ret, None]:
    semaphore = asyncio.Semaphore(limit)

    async def run_func_with_semaphore(*args: Any) -> T_Ret:
        async with semaphore:
            return await func(*args)

    tasks = [run_func_with_semaphore(*args) for args in args_list]
    for future in asyncio.as_completed(tasks):
        yield await future
