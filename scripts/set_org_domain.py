from core.storage.mongo.mongo_storage import MongoStorage
from core.utils import no_op


async def set_domain_for_all_org_settings(storage: MongoStorage):
    task_variants_collection = storage._task_variants_collection  # pyright: ignore [reportPrivateUsage]
    org_collection = storage._organization_collection  # pyright: ignore [reportPrivateUsage]

    all_tenants = [
        a["_id"]
        async for a in task_variants_collection.aggregate(
            [
                {"$group": {"_id": "$tenant"}},
            ],
        )
    ]

    for tenant in all_tenants:
        # replace all non letter or digits with "-"
        slugified_tenant = "".join([c if c.isalnum() else "-" for c in tenant])
        await org_collection.update_one(
            {"tenant": tenant},
            {"$set": {"domain": tenant, "slug": slugified_tenant}},
            upsert=True,
        )


if __name__ == "__main__":
    import asyncio

    from dotenv import load_dotenv

    load_dotenv(override=True)

    storage = MongoStorage(tenant="", encryption=no_op.NoopEncryption(), event_router=no_op.event_router)

    asyncio.run(set_domain_for_all_org_settings(storage))
