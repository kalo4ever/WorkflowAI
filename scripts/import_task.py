from typing import Annotated, Any

import typer
from pymongo.errors import DuplicateKeyError

from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.mongo_storage import MongoStorage

from ._common import get_mongo_storage, parse_db_env


class _Importer:
    def __init__(self, from_storage: MongoStorage, to_storage: MongoStorage):
        self.from_storage = from_storage
        self.to_storage = to_storage

    async def _copy_resources(self, filter: dict[str, Any], col_name: str, commit: bool):
        filter = {k: v for k, v in filter.items() if v is not None}

        from_collection = self.from_storage._get_collection(col_name)  # pyright: ignore [reportPrivateUsage]
        to_collection = self.to_storage._get_collection(col_name)  # pyright: ignore [reportPrivateUsage]

        count = 0
        async for resource in from_collection.find({**filter, "tenant": self.from_storage.tenant}):
            try:
                resource["tenant"] = self.to_storage.tenant
                if isinstance(resource["_id"], str):
                    resource["_id"] = PyObjectID.new()
                else:
                    del resource["_id"]
                if commit:
                    await to_collection.insert_one(resource)
                count += 1
            except DuplicateKeyError as e:
                print(f"Resource {resource['_id']} already exists in the target collection.", e)  # noqa: T201
                continue

        print(f"Copied {count} resources in {col_name}")  # noqa: T201

    _IGNORED_COLLECTIONS = {"org_settings", "migrations", "task_runs"}

    def _collection_filter(self, col_name: str, task_id: str) -> dict[str, Any]:
        match col_name:
            case "tasks" | "task_schema_id" | "task_inputs":
                return {"slug": task_id}
            case "task_runs" | "task_examples":
                return {"task.id": task_id}
            case _:
                return {"task_id": task_id}

    async def import_task(self, task_id: str, task_schema_id: int | None, import_run: bool, commit: bool):
        collections = await self.from_storage._db.list_collection_names()  # pyright: ignore [reportPrivateUsage]
        for col_name in collections:
            if col_name in self._IGNORED_COLLECTIONS:
                continue
            filter = self._collection_filter(col_name, task_id)

            await self._copy_resources(filter, col_name, commit)

        if import_run:
            filter: dict[str, Any] = {"task.id": task_id}
            if task_schema_id:
                filter["task.schema_id"] = task_schema_id
            await self._copy_resources(filter, "task_runs", commit)


async def import_task(
    task_id: str,
    from_storage: MongoStorage,
    to_storage: MongoStorage,
    import_run: bool,
    task_schema_id: int | None,
    commit: bool,
):
    importer = _Importer(from_storage, to_storage)

    await importer.import_task(task_id, task_schema_id=task_schema_id, import_run=import_run, commit=commit)


def parse_from_to(val: str):
    splits = val.split(":")
    if len(splits) != 2:
        raise typer.Abort(f"Invalid split: {val}")

    (staging, prod) = parse_db_env(splits[0])

    tenant = splits[1]

    return get_mongo_storage(prod, staging, tenant)


def _main(
    task_id: str,
    from_: Annotated[str, typer.Option("--from", help="env:tenant e-g prod:workflowai.com", prompt=True)],
    to: Annotated[str, typer.Option("--to", help="env:tenant e-g prod:workflowai.com", prompt=True)],
    import_run: bool = False,
    task_schema_id: Annotated[int | None, typer.Option()] = None,
    commit: bool = False,
):
    import asyncio

    from_storage = parse_from_to(from_)
    to_storage = parse_from_to(to)

    asyncio.run(
        import_task(
            task_id,
            from_storage,
            to_storage,
            import_run=import_run,
            task_schema_id=task_schema_id,
            commit=commit,
        ),
    )


if __name__ == "__main__":
    from dotenv import load_dotenv  # pyright: ignore [reportUnknownVariableType]

    load_dotenv(override=True)
    typer.run(_main)
