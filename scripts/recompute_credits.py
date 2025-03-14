import typer
from rich import print

from core.storage import ObjectNotFoundException
from core.storage.mongo.mongo_storage import MongoStorage
from core.utils import no_op


async def compute_credits_for_tenant(storage: MongoStorage, tenant: str, commit: bool):
    try:
        org = await storage.organizations.get_organization()
        added_credits = org.added_credits_usd
        current_credits = org.current_credits_usd
    except ObjectNotFoundException:
        added_credits = 0
        current_credits = 0

    agg = await anext(
        storage._task_runs_collection.aggregate(  # pyright: ignore [reportPrivateUsage]
            [
                {"$match": {"tenant": tenant, "is_free": {"$ne": True}, "config_id": {"$exists": False}}},
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$cost_usd"},
                    },
                },
            ],
        ),
    )

    print(f"Total cost for {tenant}: {agg['total']}")
    print(f"Previous cost: {added_credits - current_credits}")

    if not commit:
        return

    await storage._organization_collection.update_one(  # pyright: ignore [reportPrivateUsage]
        {"tenant": tenant},
        {
            "$set": {
                "current_credits_usd": added_credits - agg["total"],
            },
        },
    )


def _main(tenant: str, commit: bool = False):
    import asyncio

    storage = MongoStorage(tenant=tenant, encryption=no_op.NoopEncryption(), event_router=no_op.event_router)

    asyncio.run(compute_credits_for_tenant(storage, tenant, commit=commit))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(override=True)
    typer.run(_main)
