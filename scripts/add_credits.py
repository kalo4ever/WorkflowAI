import typer
from rich import print

from core.storage.mongo.mongo_storage import MongoStorage
from core.utils import no_op


async def add_credits_to_tenant(storage: MongoStorage, tenant: str, credits: float):
    doc = await storage._organization_collection.find_one_and_update(  # pyright: ignore [reportPrivateUsage]
        {"tenant": tenant},
        {
            "$inc": {
                "added_credits_usd": credits,
                "current_credits_usd": credits,
            },
        },
        return_document=True,
    )
    assert doc

    print(f"Added {credits} credits to {tenant}.")
    print(f"Current credits: {doc['current_credits_usd']}")
    print(f"Total added credits: {doc['added_credits_usd']}")


def _main(tenant: str, credits: float):
    import asyncio

    storage = MongoStorage(tenant=tenant, encryption=no_op.NoopEncryption(), event_router=no_op.event_router)

    asyncio.run(add_credits_to_tenant(storage, tenant, credits))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(override=True)

    typer.run(_main)
