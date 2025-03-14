import asyncio
from typing import Annotated

import typer
from redis.asyncio import Redis

from ._common import PROD_ARG, STAGING_ARG, prefixed_var


async def handle_key(client: Redis, key: bytes, threshold: int, commit: bool):
    key_str = key.decode("utf-8", errors="replace")

    # Skip if the key is exactly "taskiq"
    if key_str == "taskiq":
        return

    # Get idle time (in seconds) since last access
    idle_time = await client.object("idletime", key)  # pyright: ignore [reportUnknownMemberType]
    # idle_time will be None if the key doesn't exist or some error occurred
    if idle_time is not None and idle_time > threshold:
        print(f"Deleting key: {key_str} (idle time: {idle_time} seconds)")
        if commit:
            await client.delete(key)


async def cleanup_redis(dsn: str, threshold: int, commit: bool) -> None:
    client = Redis.from_url(dsn)  # pyright: ignore [reportUnknownMemberType]

    try:
        await client.execute_command("MEMORY PURGE")  # pyright: ignore [reportUnknownMemberType]

        cursor: int = 0
        while True:
            cursor, keys = await client.scan(cursor=cursor, match="*", count=100)  # pyright: ignore [reportUnknownMemberType]

            async with asyncio.TaskGroup() as tg:
                for key in keys:
                    tg.create_task(handle_key(client, key, threshold, commit))  # pyright: ignore [reportUnknownArgumentType]

            if cursor == 0:
                # No more keys left to scan
                break
    finally:
        await client.aclose()


def _cmd(
    prod: PROD_ARG,
    staging: STAGING_ARG,
    threshold: Annotated[int, typer.Option()] = 60 * 60 * 24 * 7,  # 7 days
    commit: Annotated[bool, typer.Option()] = False,
):
    dsn = prefixed_var(staging=staging, prod=prod, var="REDIS_URI")
    asyncio.run(cleanup_redis(dsn, threshold, commit))


if __name__ == "__main__":
    typer.run(_cmd)
