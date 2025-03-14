import asyncio
import logging
from typing import Any

import typer
from dotenv import load_dotenv
from pymongo import UpdateOne

from core.storage.mongo.mongo_storage import MongoStorage
from core.utils import no_op

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_group(task_runs_collection: Any, group: dict[str, Any]) -> UpdateOne | None:
    pipeline = {
        "tenant": group["tenant"],
        "task.id": group["task_id"],
        "task.schema_id": group["task_schema_id"],
        "group.iteration": group["iteration"] if "iteration" in group else {"$exists": False},
        "status": {"$in": ["success", "failure"]},
    }

    # cursor = task_runs_collection.aggregate(pipeline, hint="fetch_by_iteration")
    run_count = await task_runs_collection.count_documents(pipeline, hint="fetch_by_iteration")
    # result = [doc async for doc in cursor]

    if run_count > 0:
        logger.info(
            f"Prepared update for task {group['task_id']}/{group['task_schema_id']}#{group['iteration']}: {run_count}",
        )
        return UpdateOne({"_id": group["_id"]}, {"$set": {"run_count": run_count}})
    return None


async def update_run_counts(storage: MongoStorage):
    task_runs_collection = storage._task_runs_collection  # pyright: ignore [reportPrivateUsage]
    task_run_groups = storage._task_run_group_collection  # pyright: ignore [reportPrivateUsage]

    groups: list[dict[str, Any]] = [group async for group in task_run_groups.find({})]
    logger.info(f"Processing {len(groups)} task groups")

    operations = await asyncio.gather(
        *(process_group(task_runs_collection, group) for group in groups),
    )

    bulk_operations = [op for op in operations if op is not None]
    if bulk_operations:
        result: Any = await task_run_groups.bulk_write(bulk_operations)
        logger.info(
            "Bulk updated task groups",
            extra={"modified_count": result.modified_count},
        )

    logger.info("Run counts updated successfully")


def _main():
    storage = MongoStorage(tenant="", encryption=no_op.NoopEncryption(), event_router=no_op.event_router)
    asyncio.run(update_run_counts(storage))


if __name__ == "__main__":
    load_dotenv(override=True)
    typer.run(_main)
