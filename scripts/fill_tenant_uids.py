import asyncio
from typing import Annotated, Any

import typer
from dotenv import load_dotenv

from core.storage.mongo.mongo_storage import MongoStorage

from ._common import PROD_ARG, STAGING_ARG, get_mongo_storage


async def _fill_tenant_uids_in_collection(storage: MongoStorage, collection: str, tenant: str | None, commit: bool):
    filter: dict[str, Any] = {
        "tenant_uid": {"$exists": False},
    }
    if tenant:
        filter["tenant"] = tenant

    mongo_col = storage._get_collection(collection)  # pyright: ignore [reportPrivateUsage]

    missing_tenants = await mongo_col.distinct("tenant", filter)

    if not commit:
        count = await mongo_col.count_documents(filter)
        print(f"Found {count} missing tenant uids for {collection} and {len(missing_tenants)} distinct tenants")
        print(missing_tenants)
        return

    print(f"Mapping {len(missing_tenants)} tenants for {collection}")

    tenant_mapping = {
        doc["tenant"]: doc["uid"]
        async for doc in storage._organization_collection.find({"tenant": {"$in": missing_tenants}})  # pyright: ignore [reportPrivateUsage]
    }

    for tenant_slug, tenant_uid in tenant_mapping.items():
        await mongo_col.update_many(
            {"tenant": tenant_slug, "tenant_uid": {"$exists": False}},
            {"$set": {"tenant_uid": tenant_uid}},
        )


_skip_collections = {
    "org_settings",
    "migrations",
    "task_runs",
}


async def _fill_tenant_uids(storage: MongoStorage, collection: str | None, tenant: str | None, commit: bool):
    if collection:
        await _fill_tenant_uids_in_collection(storage, collection, tenant, commit)
        return

    collections = set(await storage._db.list_collection_names())  # pyright: ignore [reportPrivateUsage]
    collections.difference_update(_skip_collections)

    for collection in collections:
        await _fill_tenant_uids_in_collection(storage, collection, tenant, commit)


def _run(
    prod: PROD_ARG,
    staging: STAGING_ARG,
    collection: Annotated[str | None, typer.Option()] = None,
    commit: Annotated[bool, typer.Option()] = False,
    tenant: Annotated[str | None, typer.Option()] = None,
):
    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant="__system__")

    asyncio.run(_fill_tenant_uids(mongo_storage, collection, tenant, commit))


if __name__ == "__main__":
    from api.common import setup_logs

    setup_logs()

    load_dotenv(override=True)
    typer.run(_run)
