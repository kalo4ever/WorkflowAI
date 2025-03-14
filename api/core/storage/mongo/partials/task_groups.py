import asyncio
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from bson import ObjectId

from core.domain.errors import DuplicateValueError, InternalError
from core.domain.major_minor import MajorMinor
from core.domain.task_group import TaskGroup, TaskGroupFields, TaskGroupIdentifier, TaskGroupQuery
from core.domain.task_group_update import TaskGroupUpdate
from core.domain.users import UserIdentifier
from core.domain.version_major import VersionMajor
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.task_group import TaskGroupDocument
from core.storage.mongo.models.user_identifier import UserIdentifierSchema
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage, TenantTuple
from core.storage.mongo.partials.task_group_semvers import TaskGroupSemverStorage
from core.storage.mongo.utils import projection
from core.utils.dicts import exclude_keys


class MongoTaskGroupStorage(PartialStorage[TaskGroupDocument]):
    def __init__(
        self,
        tenant: TenantTuple,
        collection: AsyncCollection,
        task_group_semvers_storage: TaskGroupSemverStorage,
    ):
        super().__init__(tenant, collection, TaskGroupDocument)
        self._task_group_semvers_storage = task_group_semvers_storage

    def _task_group_by_iteration_filter(self, task_id: str, task_schema_id: int, iteration: int):
        return {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "iteration": iteration,
        }

    def _task_group_by_id_filter(self, task_id: str, id: TaskGroupIdentifier):
        if isinstance(id, MajorMinor):
            return {
                "task_id": task_id,
                "major": id.major,
                "minor": id.minor,
            }
        return {
            "task_id": task_id,
            "hash": id,
        }

    async def get_task_group_by_iteration(self, task_id: str, task_schema_id: int, iteration: int) -> TaskGroup:
        group = await self._find_one(self._task_group_by_iteration_filter(task_id, task_schema_id, iteration))
        return group.to_resource()

    @classmethod
    def _projection(cls, include: Iterable[TaskGroupFields] | None = None):
        if not include:
            return None
        mapping: dict[TaskGroupFields, list[str]] = {"id": ["hash"], "semver": ["major", "minor"]}
        i: list[str] = []
        for f in include:
            i.extend(mapping.get(f, [f]))
        # iteration is required when deserializing
        # TODO[versionsv1]: remove this once we no longer need to support iterations
        i.append("iteration")
        return projection(include=i)

    async def get_task_group_by_id(
        self,
        task_id: str,
        id: TaskGroupIdentifier,
        include: Iterable[TaskGroupFields] | None = None,
    ) -> TaskGroup:
        try:
            group = await self._find_one(
                self._task_group_by_id_filter(task_id, id),
                projection=self._projection(include=include),
            )
        except ObjectNotFoundException:
            raise ObjectNotFoundException(f"Agent version '{id}' not found for '{task_id}'", code="version_not_found")
        return group.to_resource()

    async def increment_run_count(self, task_id: str, task_schema_id: int, iteration: int, increment: int):
        await self._update_one(
            self._task_group_by_iteration_filter(task_id, task_schema_id, iteration),
            {"$inc": {"run_count": increment}},
        )

    async def _update_task_group(
        self,
        filter: dict[str, Any],
        update: TaskGroupUpdate,
        user: UserIdentifier | None,
    ) -> TaskGroup:
        u: defaultdict[str, dict[str, Any]] = defaultdict(dict)

        # Alias addition and removal handling
        if update.add_alias or update.remove_alias:
            raise InternalError("Updating a group alias is no longer supported")

        # Update 'is_favorite' field
        if update.is_favorite is not None:
            if update.is_favorite:
                u["$set"]["is_favorite"] = True
                u["$set"]["favorited_by"] = user.model_dump() if user else None
            else:
                u["$unset"]["is_favorite"] = ""

        # Update 'notes' field
        if update.notes is not None:
            if update.notes == "":
                u["$unset"]["notes"] = ""
            else:
                u["$set"]["notes"] = update.notes

        # Update 'last_active_at' field
        if update.last_active_at is not None:
            u["$set"]["last_active_at"] = update.last_active_at

        # Early exit if no updates are necessary
        if not u:
            return (await self._find_one(filter)).to_resource()

        # Perform the update
        res = await self._find_one_and_update(filter, dict(u), return_document=True, projection=None)

        return res.to_resource()

    async def update_task_group_by_id(
        self,
        task_id: str,
        id: TaskGroupIdentifier,
        update: TaskGroupUpdate,
        user: UserIdentifier | None = None,
    ) -> TaskGroup:
        filter = self._task_group_by_id_filter(task_id, id)
        return await self._update_task_group(filter, update, user)

    async def update_task_group(  # noqa: C901
        self,
        task_id: str,
        task_schema_id: int,
        iteration: int,
        update: TaskGroupUpdate,
        user: UserIdentifier | None = None,
    ) -> TaskGroup:
        id_filter = self._task_group_by_iteration_filter(task_id, task_schema_id, iteration)
        return await self._update_task_group(id_filter, update, user)

    def _filter_for_iterations(self, task_id: str, task_schema_id: int, iterations: set[int]) -> dict[str, Any]:
        filter: dict[str, Any] = {"task_id": task_id, "task_schema_id": task_schema_id}
        if len(iterations) == 1:
            filter["iteration"] = next(iter(iterations))
        else:
            filter["iteration"] = {"$in": list(iterations)}
        return filter

    async def add_benchmark_for_dataset(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        iterations: set[int],
    ):
        if not iterations or not dataset_id:
            return

        await self._update_many(
            self._filter_for_iterations(task_id, task_schema_id, iterations),
            {"$addToSet": {"benchmark_for_datasets": dataset_id}},
        )

    async def remove_benchmark_for_dataset(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        iterations: set[int],
    ):
        if not iterations or not dataset_id:
            return

        filter = self._filter_for_iterations(task_id, task_schema_id, iterations)
        filter["benchmark_for_datasets"] = dataset_id
        await self._update_many(
            filter,
            {"$pull": {"benchmark_for_datasets": dataset_id}},
        )

    async def list_task_groups(
        self,
        query: TaskGroupQuery,
        include: Iterable[TaskGroupFields] | None = None,
    ):
        filter = TaskGroupDocument.build_filter(query)
        sort = TaskGroupDocument.build_sort(query)

        async for group in self._find(
            filter,
            projection=self._projection(include=include),
            sort=sort,
            limit=query.limit,
        ):
            yield group.to_resource()

    async def first_id_for_schema(self, task_id: str, schema_id: int) -> str | None:
        filter = self._tenant_filter(
            {
                "task_id": task_id,
                "task_schema_id": schema_id,
            },
        )
        doc = await self._collection.find_one(filter, sort=[("_id", 1)], projection={"hash": 1})
        if doc is None:
            return None

        return doc["hash"]

    async def get_latest_group_iteration(
        self,
        task_id: str,
        task_schema_id: int,
    ) -> TaskGroup | None:
        filter = self._tenant_filter(
            {
                "task_id": task_id,
                "task_schema_id": task_schema_id,
            },
        )

        try:
            doc = await self._find_one(filter, sort=[("iteration", -1)])
        except ObjectNotFoundException:
            return None

        return doc.to_resource()

    async def get_previous_major(
        self,
        task_id: str,
        task_schema_id: int,
        major: int,
    ) -> TaskGroup | None:
        filter = {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "major": {
                "$exists": True,
                "$lt": major,
            },
        }
        try:
            doc = await self._find_one(filter, sort=[("major", -1)])
        except ObjectNotFoundException:
            return None

        return doc.to_resource()

    async def _attempt_saving_task_group(self, task_id: str, hash: str):
        doc = await self._find_one(
            {
                "task_id": task_id,
                "hash": hash,
            },
        )
        if doc.major is not None:
            if doc.minor is None:
                self._logger.error(
                    "Data inconsistency: major version is set but minor version is not set for task group",
                    extra={"task_id": task_id, "hash": hash},
                )
            return doc.to_resource(), False

        # Otherwise we attempt assigning the semver:
        semver, created = await self._task_group_semvers_storage.assign_semantic_version(
            task_id=task_id,
            similarity_hash=doc.similarity_hash,
            properties_hash=doc.hash,
        )
        if not created:
            # This is likely due to a race condition, so we can just raise a DuplicateValueError
            # and wait for the next attempt
            raise DuplicateValueError("Semver version was not assigned but already existed")

        # Update the document by making sure the major does not already exist
        # Otherwise we will throw an ObjectNotFoundException, also likely due to a race condition
        await self._update_one(
            {"task_id": task_id, "hash": hash, "major": {"$exists": False}},
            {"$set": {"major": semver.major, "minor": semver.minor}},
        )

        doc.major = semver.major
        doc.minor = semver.minor
        return doc.to_resource(), True

    async def save_task_group(self, task_id: str, hash: str):
        exc: Exception | None = None
        MAX_RETRIES = 3
        for i in range(0, MAX_RETRIES):
            try:
                return await self._attempt_saving_task_group(task_id, hash)
            except (DuplicateValueError, ObjectNotFoundException) as e:
                if i < MAX_RETRIES - 1:
                    await asyncio.sleep(0.05)
                exc = e
        raise InternalError("Failed to save task group") from exc

    def list_version_majors(self, task_id: str, task_schema_id: int | None):
        filter: dict[str, Any] = {"task_id": task_id, "major": {"$exists": True}}
        if task_schema_id is not None:
            # task_schema_id is not in the index, but it should not have a big impact
            # since we are not dealing with a lot of data
            filter["task_schema_id"] = task_schema_id

        def _map(doc: dict[str, Any]) -> VersionMajor:
            return VersionMajor(
                similarity_hash=doc["similarity_hash"],
                schema_id=doc["schema_id"],
                major=doc["_id"],
                properties=VersionMajor.Properties.model_validate(doc["major_properties"]),
                minors=[
                    VersionMajor.Minor(
                        id=sub_version["hash"],
                        iteration=sub_version.get("iteration"),
                        minor=sub_version["minor"],
                        properties=VersionMajor.Minor.Properties.model_validate(
                            exclude_keys(sub_version["properties"], {"task_variant_id", "instructions", "temperature"}),
                        ),
                        last_active_at=sub_version.get("last_active_at"),
                        is_favorite=sub_version.get("is_favorite"),
                        favorited_by=UserIdentifierSchema.to_domain_optional(sub_version.get("favorited_by")),
                        notes=sub_version.get("notes"),
                        run_count=sub_version.get("run_count"),
                        created_by=UserIdentifierSchema.to_domain_optional(sub_version.get("created_by")),
                    )
                    for sub_version in doc["sub_versions"]
                ],
                created_by=doc["created_by"],
                created_at=ObjectId(doc["first_id"]).generation_time,
            )

        return self._aggregate(
            [
                {"$match": filter},
                # Sort will happen in memory instead of with the index
                # It's fine for now, but we might want to optimize when we migrate
                # to PSQL
                {"$sort": {"major": 1, "minor": 1}},
                {
                    "$group": {
                        "_id": "$major",
                        "schema_id": {"$first": "$task_schema_id"},
                        "similarity_hash": {"$first": "$similarity_hash"},
                        "major_properties": {"$first": "$properties"},
                        "created_by": {"$first": "$created_by"},
                        "first_id": {"$first": "$_id"},
                        "sub_versions": {
                            "$push": {
                                "iteration": "$iteration",
                                "hash": "$hash",
                                "minor": "$minor",
                                "properties": "$properties",
                                "last_active_at": "$last_active_at",
                                "is_favorite": "$is_favorite",
                                "favorited_by": "$favorited_by",
                                "notes": "$notes",
                                "run_count": "$run_count",
                                "created_by": "$created_by",
                            },
                        },
                    },
                },
                {"$sort": {"_id": 1}},
            ],
            # Can't set hint here for now
            # hint="major_minor_unique",
            map_fn=_map,
        )

    async def map_iterations(self, task_id: str, task_schema_id: int, iterations: set[int]) -> dict[int, str]:
        return {
            grp.iteration: grp.hash
            async for grp in self._find(
                self._filter_for_iterations(task_id, task_schema_id, iterations),
                projection={"hash": 1, "iteration": 1},
            )
        }
