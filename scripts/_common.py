import os
from typing import Annotated, Literal

import typer
from rich import print

from core.storage.azure.azure_blob_file_storage import AzureBlobFileStorage
from core.storage.clickhouse.clickhouse_client import ClickhouseClient
from core.storage.mongo.mongo_storage import MongoStorage
from core.utils import no_op

MONGO_DSN_VAR = "WORKFLOWAI_MONGO_CONNECTION_STRING"
CLICKHOUSE_DSN_VAR = "CLICKHOUSE_CONNECTION_STRING"
FILE_STORAGE_DSN_VAR = "WORKFLOWAI_STORAGE_CONNECTION_STRING"
FILE_STORAGE_CONTAINER_NAME_VAR = "WORKFLOWAI_STORAGE_TASK_RUNS_CONTAINER"

LOCAL_PREFIX = "LOCAL_"
STAGING_PREFIX = "STAGING_"
PROD_PREFIX = "PROD_"

DB_ENV = Literal["staging", "prod", "local"]


def parse_db_env(val: str):
    if val == "staging":
        return (True, False)
    if val == "prod":
        return (False, True)
    if val == "local":
        return (False, False)
    raise typer.Abort(f"Invalid db env: {val}")


def prefixed_var(staging: bool, prod: bool, var: str):
    if prod:
        return os.environ[f"{PROD_PREFIX}{var}"]
    if staging:
        return os.environ[f"{STAGING_PREFIX}{var}"]
    return os.environ[f"{LOCAL_PREFIX}{var}"]


def get_mongo_storage(prod: bool, staging: bool, tenant: str):
    dsn = prefixed_var(staging=staging, prod=prod, var=MONGO_DSN_VAR)
    return MongoStorage(
        connection_string=dsn,
        tenant=tenant,
        encryption=no_op.NoopEncryption(),
        event_router=no_op.event_router,
    )


def get_clickhouse_client(prod: bool, staging: bool, tenant_uid: int):
    dsn = prefixed_var(staging=staging, prod=prod, var=CLICKHOUSE_DSN_VAR)
    return ClickhouseClient(connection_string=dsn, tenant_uid=tenant_uid)


def get_file_storage(prod: bool, staging: bool, tenant: str):
    return AzureBlobFileStorage(
        connection_string=prefixed_var(staging=staging, prod=prod, var=FILE_STORAGE_DSN_VAR),
        container_name=prefixed_var(staging=staging, prod=prod, var=FILE_STORAGE_CONTAINER_NAME_VAR),
    )


def is_true(var: str | None) -> bool:
    return var in {"t", "true", "1", "y", "yes", "Y", "YES", "TRUE", "T"}


def get_current_branch() -> str:
    return os.popen("git branch --show-current").read().strip()


def is_prod_branch(branch: str) -> bool:
    return branch in {"main", "master"} or branch.startswith("release/") or branch.startswith("hotfix/")


def raise_if_not_prod_branch():
    branch = get_current_branch()
    if not is_prod_branch(branch):
        raise ValueError(f"Current branch {branch} is not a prod branch")


def env_name(prod: bool, staging: bool) -> str:
    if prod:
        return "prod"
    if staging:
        return "staging"
    return "local"


def wait_for_truthy_input(prompt: str):
    i = input(f"{prompt}? [Y/n]")
    if i and not is_true(i):
        print("Exiting")
        os.abort()


PROD_ARG = Annotated[bool, typer.Option(default_factory=lambda: is_true(os.getenv("PROD")))]
STAGING_ARG = Annotated[bool, typer.Option(default_factory=lambda: is_true(os.getenv("STAGING")))]
