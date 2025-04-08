#! /usr/bin/env python3


import asyncio
from datetime import datetime
from typing import Annotated, Any

import typer
from dotenv import load_dotenv
from rich import print

from core.domain.consts import METADATA_KEY_DEPLOYMENT_ENVIRONMENT, METADATA_KEY_DEPLOYMENT_ENVIRONMENT_DEPRECATED
from core.domain.task_run import Run
from core.storage.clickhouse.clickhouse_client import ClickhouseClient
from core.storage.clickhouse.models.runs import CLICKHOUSE_RUN_VERSION, ClickhouseRun
from core.storage.mongo.models.task_run_document import TaskRunDocument
from core.storage.mongo.mongo_storage import MongoStorage

from ._common import PROD_ARG, STAGING_ARG, get_clickhouse_client, get_mongo_storage


class Importer:
    def __init__(self, mongo_storage: MongoStorage, clickhouse_client: ClickhouseClient):
        self.mongo_storage = mongo_storage
        self.clickhouse_client = clickhouse_client
        self.run_collections = mongo_storage._task_runs_collection  # pyright: ignore [reportPrivateUsage]

        self._tenant_uid_cache = dict[str, int]()
        self._task_uid_cache = dict[tuple[str, str], int]()
        self._columns = list(ClickhouseRun.model_fields.keys())
        self._tenant_uid_lock = asyncio.Lock()
        self._task_uid_lock = asyncio.Lock()

    async def list_runs(
        self,
        tenant: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        task_id: str | None,
        task_schema_id: int | None,
        limit: int,
        run_ids: list[str] | None,
        batch_size: int,
    ):
        filter: dict[str, Any] = {
            "$or": [
                {"stored_in_clickhouse": {"$exists": False}},
                {"stored_in_clickhouse": {"$lt": CLICKHOUSE_RUN_VERSION}},  # noqa: F821
            ],
        }
        if tenant:
            filter["tenant"] = tenant
        if task_id:
            filter["task.id"] = task_id
        if task_schema_id:
            filter["task.schema_id"] = task_schema_id
        if from_date:
            filter["created_at"] = {"$gte": from_date.date()}
        if to_date:
            f = filter.setdefault("created_at", {})
            f["$lte"] = to_date.date()
        if run_ids:
            filter["_id"] = {"$in": run_ids}
        async for run in self.run_collections.find(filter).limit(limit).batch_size(batch_size):
            yield (run["tenant"], TaskRunDocument.model_validate(run).to_resource())

    async def get_tenant_uid(self, tenant: str) -> int:
        async with self._tenant_uid_lock:
            try:
                return self._tenant_uid_cache[tenant]
            except KeyError:
                pass
            tenant_doc = await self.mongo_storage._organization_collection.find_one({"tenant": tenant})  # pyright: ignore [reportPrivateUsage]
            assert tenant_doc is not None
            tenant_uid = tenant_doc["uid"]
            assert tenant_uid > 0
            self._tenant_uid_cache[tenant] = tenant_uid
            return tenant_uid

    async def get_task_uid(self, tenant: str, task_id: str) -> int:
        async with self._task_uid_lock:
            try:
                return self._task_uid_cache[(tenant, task_id)]
            except KeyError:
                pass
            task_doc = await self.mongo_storage._tasks_collection.find_one({"tenant": tenant, "task_id": task_id})  # pyright: ignore [reportPrivateUsage]
            if not task_doc:
                print("Skipping task", tenant, task_id)
                self._task_uid_cache[(tenant, task_id)] = 0
                return 0
            assert task_doc is not None
            task_uid = task_doc["uid"]
            assert task_uid > 0
            self._task_uid_cache[(tenant, task_id)] = task_uid
            return task_uid

    async def _convert_run_to_columns(self, tenant: str, run: Run):
        tenant_uid = await self.get_tenant_uid(tenant)
        task_uid = await self.get_task_uid(tenant, run.task_id)
        if task_uid == 0:
            raise ValueError("Task not found", tenant, run.task_id)
        if run.task_schema_id < 0:
            print("Run had invalid task schema id", tenant, run.task_id)
            raise ValueError("Run had invalid task schema id", tenant, run.task_id)
        run.task_uid = task_uid

        clickhouse_run = ClickhouseRun.from_domain(tenant_uid, run)
        # Sanitize the metadata:
        if clickhouse_run.metadata:
            if METADATA_KEY_DEPLOYMENT_ENVIRONMENT_DEPRECATED in clickhouse_run.metadata:
                value = str(clickhouse_run.metadata.pop(METADATA_KEY_DEPLOYMENT_ENVIRONMENT_DEPRECATED)).removeprefix(
                    "environment=",
                )
                clickhouse_run.metadata[METADATA_KEY_DEPLOYMENT_ENVIRONMENT] = value

        dumped = clickhouse_run.model_dump()
        return [dumped[column] for column in self._columns]

    async def store_runs_on_clickhouse(self, runs: list[tuple[str, Run]], commit: bool):
        # We could do a gather here, but it would require making the
        data = await asyncio.gather(
            *(self._convert_run_to_columns(tenant, run) for tenant, run in runs),
            return_exceptions=True,
        )
        data = [d for d in data if not isinstance(d, BaseException)]
        if not data:
            return 0

        if not commit:
            return len(data)

        client = await self.clickhouse_client.client()
        try:
            await client.insert(
                table="runs",
                column_names=self._columns,
                data=data,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert run  into clickhouse {[run.id for _, run in runs]}") from e
        run_ids = [run.id for _, run in runs]
        await self.mongo_storage._task_runs_collection.update_many(  # pyright: ignore [reportPrivateUsage]
            {"_id": {"$in": run_ids}},
            {"$set": {"stored_in_clickhouse": CLICKHOUSE_RUN_VERSION}},
        )
        return len(data)

    async def import_runs(
        self,
        tenant: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        task_id: str | None,
        task_schema_id: int | None,
        limit: int,
        commit: bool,
        run_ids: list[str] | None,
        batch_size: int,
    ):
        count = 0
        agg: list[tuple[str, Run]] = []
        async for current_tenant, run in self.list_runs(
            tenant,
            from_date,
            to_date,
            task_id,
            task_schema_id,
            run_ids=run_ids,
            limit=limit,
            batch_size=batch_size,
        ):
            agg.append((current_tenant, run))
            if len(agg) >= batch_size:
                count += await self.store_runs_on_clickhouse(agg, commit)
                agg = []
                print(f"Imported {count} runs")

        if agg:
            count += await self.store_runs_on_clickhouse(agg, commit)

        print(f"Imported total {count} runs")


def _run(
    staging: STAGING_ARG,
    prod: PROD_ARG,
    tenant: Annotated[str | None, typer.Option()] = None,
    from_date: Annotated[datetime | None, typer.Option()] = None,
    to_date: Annotated[datetime | None, typer.Option()] = None,
    task_id: Annotated[str | None, typer.Option()] = None,
    task_schema_id: Annotated[int | None, typer.Option()] = None,
    limit: Annotated[int, typer.Option()] = 1000,
    commit: Annotated[bool, typer.Option()] = False,
    run_ids: Annotated[list[str] | None, typer.Option()] = None,
    batch_size: Annotated[int, typer.Option()] = 50,
):
    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant="__system__")
    clickhouse_client = get_clickhouse_client(prod=prod, staging=staging, tenant_uid=0)
    importer = Importer(mongo_storage, clickhouse_client)
    asyncio.run(
        importer.import_runs(
            tenant=tenant,
            task_id=task_id,
            task_schema_id=task_schema_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            commit=commit,
            run_ids=run_ids,
            batch_size=batch_size,
        ),
    )


if __name__ == "__main__":
    load_dotenv(override=True)
    typer.run(_run)
