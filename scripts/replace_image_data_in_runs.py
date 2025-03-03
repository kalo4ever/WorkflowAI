import asyncio
import binascii
import json
from datetime import datetime
from typing import Annotated, Any

import typer
from dotenv import load_dotenv

from api.services.runs import RunsService
from core.runners.workflowai.utils import FileWithKeyPath, extract_files
from core.storage.azure.azure_blob_file_storage import AzureBlobFileStorage
from core.storage.mongo.mongo_storage import MongoStorage

from ._common import PROD_ARG, STAGING_ARG, get_file_storage, get_mongo_storage


class Sanitizer:
    def __init__(self, storage: MongoStorage, file_storage: AzureBlobFileStorage):
        self.storage = storage
        self.file_storage = file_storage

    async def _list_task_schemas(self, tenant: str | None, task_id: str | None, task_schema_id: int | None):
        match = {}
        if tenant:
            match["tenant"] = tenant
        if task_id:
            match["slug"] = task_id
        if task_schema_id:
            match["schema_id"] = task_schema_id
        schemas = self.storage._task_variants_collection.aggregate(  # pyright: ignore [reportPrivateUsage]
            [
                {
                    "$match": match,
                },
                {
                    "$group": {
                        "_id": {
                            "tenant": "$tenant",
                            "task_id": "$slug",
                            "schema_id": "$schema_id",
                        },
                        "input_schema": {
                            "$first": "$input_schema.json_schema",
                        },
                    },
                },
            ],
        )
        async for schema in schemas:
            if "$defs" in schema["input_schema"] and "Image" in schema["input_schema"]["$defs"]:
                yield {
                    "tenant": schema["_id"]["tenant"],
                    "task_id": schema["_id"]["task_id"],
                    "task_schema_id": schema["_id"]["schema_id"],
                    "input_schema": schema["input_schema"],
                }

    async def _list_runs(
        self,
        tenant: str,
        task_id: str,
        task_schema_id: int,
        from_date: datetime | None,
        to_date: datetime | None,
        key_paths: list[str] | None,
    ):
        match: dict[str, Any] = {
            "tenant": tenant,
            "task.id": task_id,
            "task.schema_id": task_schema_id,
        }
        if from_date:
            match["created_at"] = {
                "$gte": from_date,
            }
        if to_date:
            match["created_at"] = {
                "$lte": to_date,
            }

        if key_paths:
            match["$or"] = [{f"task_input.{k}.data": {"$exists": True}} for k in key_paths]

        async for run in self.storage._task_runs_collection.find(match, projection={"_id": 1, "task_input": 1}):  # pyright: ignore [reportPrivateUsage]
            yield run

    def _file_key_paths(self, input_schema: dict[str, Any]) -> list[str]:
        """Find all key paths in a JSON schema that reference the Image definition.

        Args:
            input_schema: The JSON schema to search through

        Returns:
            A list of key paths (dot-separated strings) where Image references are found
        """
        paths: list[str] = []

        def _traverse(schema: dict[str, Any], current_path: list[str]) -> None:
            # Check if this node references an Image
            if schema.get("$ref") == "#/$defs/Image":
                paths.append(".".join(current_path))
                return

            # For arrays, we need to check the items schema
            if schema.get("type") == "array" and "items" in schema:
                _traverse(schema["items"], current_path)
                return

            # For objects, traverse all properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    _traverse(prop_schema, [*current_path, prop_name])

            # Handle anyOf, allOf, oneOf
            for key in ["anyOf", "allOf", "oneOf"]:
                if key in schema:
                    for sub_schema in schema[key]:
                        _traverse(sub_schema, current_path)

        _traverse(input_schema, [])
        return paths

    async def _store_files(
        self,
        folder_path: str,
        files: list[FileWithKeyPath],
    ):
        for file in files:
            if not file.data:
                # Skipping, only reason a file might not have data is if it's private
                continue

            try:
                file.storage_url = await self.file_storage.store_file(file, folder_path=folder_path)
            # Only catch for base64 decode error
            except binascii.Error:
                print("Stripping data for run since it's not base64 encoded")
                file.data = None

        return files

    async def _sanitize_input(
        self,
        tenant: str,
        task_id: str,
        run_id: str,
        input_schema: dict[str, Any],
        task_input: dict[str, Any],
        commit: bool,
    ):
        try:
            _, _, files = extract_files(input_schema, task_input)
        except Exception as e:
            print(f"Error extracting files for run {run_id}", e)
            return False

        files = [file for file in files if file.data]

        if not files:
            return False

        folder_path = f"{tenant}/{task_id}"

        # print(f"Storing {len(files)} files to {folder_path}")
        if commit:
            await self._store_files(folder_path, files)  # pyright: ignore [reportPrivateUsage]
        else:
            for file in files:
                file.storage_url = "blabla" * 10

        for file in files:
            file.data = None

        await RunsService._apply_files(task_input, files, {"content_type", "url", "storage_url"}, exclude={"key_path"})  # pyright: ignore [reportPrivateUsage]

        return True

    async def _sanitize_run(self, tenant: str, task_id: str, schema: dict[str, Any], run: dict[str, Any], commit: bool):
        task_input = run["task_input"]
        size_before = len(json.dumps(run["task_input"]).encode("utf-8"))
        should_sanitize = await self._sanitize_input(
            tenant,
            task_id,
            run_id=run["_id"],
            input_schema=schema,
            task_input=task_input,
            commit=commit,
        )
        if not should_sanitize:
            return 0

        size_after = len(json.dumps(task_input).encode("utf-8"))

        print(
            f"Sanitizing run {run['_id']} for tenant {tenant} task {task_id} from {size_before} to {size_after}",
        )

        if commit:
            await self.storage._task_runs_collection.update_one(  # pyright: ignore [reportPrivateUsage]
                {"_id": run["_id"]},
                {"$set": {"task_input": task_input}},
            )

        return size_after - size_before

    async def _sanitize_task_schema(
        self,
        tenant: str,
        task_id: str,
        task_schema_id: int,
        schema: dict[str, Any],
        remaining_max_runs: int,
        commit: bool,
        from_date: datetime | None,
        to_date: datetime | None,
    ):
        key_paths = self._file_key_paths(schema)
        if not key_paths:
            # This can happen if the task has an image definition inside a ref
            # print("No key paths found")
            return remaining_max_runs, 0
        # print("Checking for files in", key_paths)
        sanitized_count = 0
        total_saved = 0
        async for run in self._list_runs(
            tenant,
            task_id,
            task_schema_id,
            from_date=from_date,
            to_date=to_date,
            key_paths=key_paths,
        ):
            sanitized = await self._sanitize_run(tenant, task_id, schema, run, commit)
            if sanitized != 0:
                total_saved += sanitized
                sanitized_count += 1
                if sanitized_count >= remaining_max_runs:
                    break

        print(f"Sanitized {sanitized_count} runs for tenant {tenant} task {task_id}/{task_schema_id}")
        return remaining_max_runs - sanitized_count, total_saved

    async def sanitize_inputs(
        self,
        tenant: str | None,
        task_id: str | None,
        task_schema_id: int | None,
        from_date: datetime | None,
        to_date: datetime | None,
        commit: bool,
        max_runs: int,
    ):
        remaining_max_runs = max_runs
        total_saved = 0
        async for task_schema in self._list_task_schemas(tenant, task_id, task_schema_id):
            print(f"Sanitizing task {task_schema['tenant']}/{task_schema['task_id']}/{task_schema['task_schema_id']}")
            remaining_max_runs, total_saved_for_schema = await self._sanitize_task_schema(
                tenant=task_schema["tenant"],
                task_id=task_schema["task_id"],
                task_schema_id=task_schema["task_schema_id"],
                schema=task_schema["input_schema"],
                remaining_max_runs=remaining_max_runs,
                commit=commit,
                from_date=from_date,
                to_date=to_date,
            )
            total_saved += total_saved_for_schema
            print(f"Remaining max runs: {remaining_max_runs}")

            if remaining_max_runs <= 0:
                break

        print(f"Total saved: {round(total_saved / 1024 / 1024, 2)} MB")


def _run(
    staging: STAGING_ARG,
    prod: PROD_ARG,
    tenant: Annotated[str | None, typer.Option()] = None,
    from_date: Annotated[datetime | None, typer.Option()] = None,
    task_id: Annotated[str | None, typer.Option()] = None,
    task_schema_id: Annotated[int | None, typer.Option()] = None,
    to_date: Annotated[datetime | None, typer.Option()] = None,
    max_runs: Annotated[int, typer.Option()] = 5,
    commit: Annotated[bool, typer.Option()] = False,
):
    mongo_storage = get_mongo_storage(prod=prod, staging=staging, tenant="")
    file_storage = get_file_storage(prod=prod, staging=staging, tenant="")
    sanitizer = Sanitizer(mongo_storage, file_storage)
    asyncio.run(
        sanitizer.sanitize_inputs(tenant, task_id, task_schema_id, from_date, to_date, commit, max_runs=max_runs),
    )


if __name__ == "__main__":
    load_dotenv(override=True)
    typer.run(_run)
