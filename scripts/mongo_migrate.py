import asyncio
import logging
from typing import Annotated

import typer
from dotenv import load_dotenv

from _common import (
    PROD_ARG,
    STAGING_ARG,
    env_name,
    get_mongo_storage,
    raise_if_not_prod_branch,
    wait_for_truthy_input,
)
from core.storage.mongo.migrations.migrate import check_migrations, migrate


def _migrate_command(
    prod: PROD_ARG,
    staging: STAGING_ARG,
    max_retries: Annotated[int, typer.Option()] = 50,
    commit: Annotated[bool, typer.Option()] = False,
):
    if prod:
        raise_if_not_prod_branch()

    logging.info(f"Migrating {env_name(prod, staging)}" + "?" if commit else "")
    if commit:
        wait_for_truthy_input("Continue")

    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant="__system__")

    async def _inner():
        if commit:
            await migrate(mongo_storage, max_retries=max_retries)
        else:
            await check_migrations(mongo_storage)

    asyncio.run(_inner())


if __name__ == "__main__":
    from api.common import setup_logs

    setup_logs()

    load_dotenv(override=True)
    typer.run(_migrate_command)
