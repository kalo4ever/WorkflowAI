import asyncio
from typing import Annotated, Any

import typer
from dotenv import load_dotenv

from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection

from ._common import PROD_ARG, STAGING_ARG, get_mongo_storage

_key_name_by_collection = {
    "tasks": "slug",
    "task_schema_id": "task_id",
}

_skip_collections = {
    "org_settings",
    "task_info",
    "task_examples",
    "task_runs",
    "transcriptions",
    "task_images",
    "migrations",
}


async def _update_with_mapping(
    collection: AsyncCollection,
    key_name: str,
    tenant: str,
    task_id: str,
    task_uid: str,
    commit: bool,
) -> None:
    filter = {
        "task_uid": {"$exists": False},
        "tenant": tenant,
        key_name: task_id,
    }

    if not commit:
        count = await collection.count_documents(filter)
        print(f"Found {count} missing task uids for {collection.name} and {tenant} and {task_id}")
        return

    res = await collection.update_many(filter, {"$set": {"task_uid": task_uid}})
    print(f"Updated {res.modified_count} documents for {collection.name} and {tenant} and {task_id}")


async def _fill_task_uids_in_collection(
    storage: MongoStorage,
    collection: str,
    task_mapping: dict[tuple[str, str], Any],
    commit: bool,
):
    mongo_col = storage._get_collection(collection)  # pyright: ignore [reportPrivateUsage]
    key_name = _key_name_by_collection.get(collection, "task_id")

    for tenant, task_id in task_mapping.keys():
        await _update_with_mapping(mongo_col, key_name, tenant, task_id, task_mapping[(tenant, task_id)], commit=commit)


async def _fill_task_uids(
    storage: MongoStorage,
    collection: str | None,
    tenant: str | None,
    commit: bool,
    task_id: str | None,
):
    task_filter: dict[str, Any] = {}
    if tenant:
        task_filter["tenant"] = tenant
    if task_id:
        task_filter["task_id"] = task_id

    task_mapping = {
        (doc["tenant"], doc["task_id"]): doc["uid"]
        async for doc in storage._tasks_collection.find(task_filter)  # pyright: ignore [reportPrivateUsage]
    }
    print(f"Mapping {len(task_mapping)} tasks")

    if collection:
        await _fill_task_uids_in_collection(storage, collection, commit=commit, task_mapping=task_mapping)
        return

    collections = set(await storage._db.list_collection_names())  # pyright: ignore [reportPrivateUsage]
    collections.difference_update(_skip_collections)

    for collection in collections:
        await _fill_task_uids_in_collection(storage, collection, commit=commit, task_mapping=task_mapping)


def _run(
    prod: PROD_ARG,
    staging: STAGING_ARG,
    collection: Annotated[str | None, typer.Option()] = None,
    task_id: Annotated[str | None, typer.Option()] = None,
    commit: Annotated[bool, typer.Option()] = False,
    tenant: Annotated[str | None, typer.Option()] = None,
):
    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant="__system__")

    asyncio.run(_fill_task_uids(mongo_storage, collection, tenant=tenant, task_id=task_id, commit=commit))


if __name__ == "__main__":
    from api.common import setup_logs

    setup_logs()

    load_dotenv(override=True)
    typer.run(_run)
