import asyncio
from datetime import datetime
from typing import Annotated, Any

import typer
from dotenv import load_dotenv

from core.storage.mongo.mongo_storage import MongoStorage

from ._common import PROD_ARG, STAGING_ARG, get_mongo_storage


async def _fix_cost_of_failed_runs(
    mongo_storage: MongoStorage,
    tenant: str,
    task_id: str | None,
    task_schema_id: int | None,
    from_date: datetime,
    to_date: datetime | None,
    commit: bool,
):
    filter: dict[str, Any] = {
        "tenant": tenant,
        "status": "failure",
        "created_at": {"$gte": from_date.date()},
        "llm_completions.0.response": "",
    }
    if task_id:
        filter["task.id"] = task_id
    if task_schema_id:
        filter["task.schema_id"] = task_schema_id
    if to_date:
        filter["created_at"]["$lte"] = to_date.date()
    print(str(filter).replace("'", '"').replace("datetime.date", "ISODate"))

    col = mongo_storage._task_runs_collection  # pyright: ignore [reportPrivateUsage]
    try:
        agg = await anext(
            col.aggregate(
                [
                    {"$match": filter},
                    {"$group": {"_id": "", "count": {"$sum": 1}, "cost": {"$sum": "$cost_usd"}}},
                ],
            ),
        )
    except StopAsyncIteration:
        print("No runs found")
        return
    total_cost = agg["cost"]
    print(f"Found {agg['count']} runs with total cost {agg['cost']}")

    if commit:
        await col.update_many(filter, {"$set": {"cost_usd": 0}})
        await mongo_storage._organization_collection.update_one(  # pyright: ignore [reportPrivateUsage]
            {"tenant": tenant},
            {
                "$inc": {
                    "current_credits_usd": total_cost,
                },
            },
        )


def _run(
    staging: STAGING_ARG,
    prod: PROD_ARG,
    tenant: Annotated[str, typer.Option()],
    from_date: Annotated[datetime, typer.Option()],
    task_id: Annotated[str | None, typer.Option()] = None,
    task_schema_id: Annotated[int | None, typer.Option()] = None,
    to_date: Annotated[datetime | None, typer.Option()] = None,
    commit: Annotated[bool, typer.Option()] = False,
):
    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant=tenant)
    asyncio.run(_fix_cost_of_failed_runs(mongo_storage, tenant, task_id, task_schema_id, from_date, to_date, commit))


if __name__ == "__main__":
    load_dotenv(override=True)
    typer.run(_run)
