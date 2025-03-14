import asyncio
from typing import Annotated, Any

import typer

from core.domain.task_io import SerializableTaskIO
from core.storage.mongo.mongo_storage import MongoStorage

from ._common import PROD_ARG, STAGING_ARG, get_mongo_storage


class SchemaIDXMappingUpdater:
    """Makes sure that the existing schema id mappings match the current schema versions.
    Useful when the way we compute schema IDs changes"""

    def __init__(self, storage: MongoStorage):
        self.storage = storage

    async def _recompute_hash_for_schema(
        self,
        tenant: str,
        task_id: str,
        task_schema_id: int,
        input_schema_id: str,
        output_schema_id: str,
    ):
        task_variant = await self.storage._task_variants_collection.find_one(  # pyright: ignore [reportPrivateUsage]
            {
                "tenant": tenant,
                "slug": task_id,
                "schema_id": task_schema_id,
                "input_schema.version": input_schema_id,
                "output_schema.version": output_schema_id,
            },
        )
        if not task_variant:
            raise ValueError(
                f"Task variant not found for tenant {tenant} and task_id {task_id} and task_schema_id {task_schema_id}",
            )
        input_io = SerializableTaskIO.from_json_schema(task_variant["input_schema"]["json_schema"], streamline=True)
        output_io = SerializableTaskIO.from_json_schema(task_variant["output_schema"]["json_schema"], streamline=True)
        return f"{input_io.version}/{output_io.version}"

    async def _update_task_schema_mapping(self, doc: dict[str, Any], schema_id: int | None, commit: bool):
        idx_mapping: dict[str, int] = doc["idx_mapping"]
        # version to schema id tuples sorted by schema id
        schema_id_tuples = sorted(idx_mapping.items(), key=lambda x: x[1])
        if schema_id:
            schema_id_tuples = [t for t in schema_id_tuples if t[1] == schema_id]

        updates: dict[str, int] = {}

        print("\n--------------------------------")
        print(f"{doc['tenant']}/{doc['slug']}")

        for version, current_schema_id in schema_id_tuples:
            splits = version.split("/")
            assert len(splits) == 2, "sanity"
            input_schema_id, output_schema_id = splits

            try:
                recomputed = await self._recompute_hash_for_schema(
                    doc["tenant"],
                    doc["slug"],
                    current_schema_id,
                    input_schema_id,
                    output_schema_id,
                )
            except ValueError:
                print(f"    Error recomputing schema {current_schema_id}")
                continue

            if recomputed == version:
                # The schema was not updated so we are good
                print("   recomputed schema is the same as the current schema")
                continue
            if recomputed in idx_mapping:
                # The schema was updated but the new schema is already in the mapping
                if idx_mapping[recomputed] != idx_mapping[version]:
                    print(
                        f"    we recomputed a schema that matches an other schema: {current_schema_id} -> {idx_mapping[version]}",
                    )
                print("    Skipping since recomputed schema is already in the mapping")
                continue
            if recomputed in updates:
                # That can happen on old schemas where both were updated. In which case we keep the latest one
                print("    we recomputed a schema that matches an other updated schema")
            updates[recomputed] = current_schema_id

        print("updates", updates)

        if not updates:
            return 0

        if commit:
            sets = {f"idx_mapping.{k}": v for k, v in updates.items()}
            await self.storage._task_schema_id_collection.update_one(  # pyright: ignore [reportPrivateUsage]
                {"_id": doc["_id"]},
                {"$set": sets},
            )

        return 1

    async def run(
        self,
        tenant: str | None,
        task_id: str | None,
        task_schema_id: int | None,
        limit: int,
        commit: bool,
    ):
        filter: dict[str, Any] = {}
        if tenant:
            filter["tenant"] = tenant
        if task_id:
            filter["slug"] = task_id

        count = 0
        async for doc in self.storage._task_schema_id_collection.find(filter):  # pyright: ignore [reportPrivateUsage]
            count += await self._update_task_schema_mapping(doc, task_schema_id, commit)
            if count >= limit:
                break


def _run(
    staging: STAGING_ARG,
    prod: PROD_ARG,
    tenant: Annotated[str | None, typer.Option()] = None,
    task_id: Annotated[str | None, typer.Option()] = None,
    task_schema_id: Annotated[int | None, typer.Option()] = None,
    limit: Annotated[int, typer.Option()] = 1000,
    commit: Annotated[bool, typer.Option()] = False,
):
    storage = get_mongo_storage(prod=prod, staging=staging, tenant="__system__")
    updater = SchemaIDXMappingUpdater(storage)
    asyncio.run(updater.run(tenant=tenant, task_id=task_id, task_schema_id=task_schema_id, limit=limit, commit=commit))


if __name__ == "__main__":
    typer.run(_run)
