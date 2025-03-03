from core.storage.mongo.migrations.base import AbstractMigration


class FirstMigration(AbstractMigration):
    async def create_task_variants_indices(self):
        await self._task_variants_collection.create_index(
            [("version", 1), ("slug", 1), ("tenant", 1)],
            name="version_and_slug",
            unique=True,
            background=True,
        )

        await self._task_variants_collection.create_index(
            [("tenant", 1), ("evaluator_for", 1)],
            name="task_evaluator_for_tenant_index",
            background=True,
            sparse=True,
        )

    async def create_task_schema_id_indices(self):
        await self._task_schema_id_collection.create_index(
            [("slug", 1), ("tenant", 1)],
            name="task_schema_id_schema_index",
            unique=True,
            background=True,
        )

    async def create_task_run_group_idx_indices(self):
        await self._task_run_group_idx_collection.create_index(
            [("tenant", 1), ("task_id", 1)],
            name="task_run_group_idx_tenant_index",
            unique=True,
            background=True,
        )

    async def create_task_run_group_indices(self):
        await self._task_run_group_collection.create_index(
            [("tenant", 1), ("alias", 1), ("task_id", 1), ("task_schema_id", 1)],
            name="alias",
            unique=True,
            background=True,
        )

        await self._task_run_group_collection.create_index(
            [("tenant", 1), ("hash", 1), ("task_id", 1), ("task_schema_id", 1)],
            name="hash",
            unique=True,
            background=True,
        )

        await self._task_run_group_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1), ("iteration", 1)],
            name="iteration_partial",
            unique=True,
            background=True,
            partialFilterExpression={"iteration": {"$exists": True}},
        )

        await self._task_run_group_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1), ("aliases", 1)],
            name="aliases",
            unique=True,
            background=False,
            partialFilterExpression={"aliases": {"$gt": []}},
        )

    async def create_task_run_indices(self):
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                ("labels", 1),
                ("created_at", -1),
                ("group.hash", 1),
                ("group.iteration", 1),
                ("example_id", 1),
            ],
            name="default",
            background=True,
        )

        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("scores.example_id", 1),
                ("scores.evaluator.id", 1),
                ("scores.evaluator.name", 1),
                ("scores.evaluator.tags", 1),
            ],
            name="task_run_scores",
            background=True,
        )

    async def create_org_settings_indices(self):
        await self._organization_collection.create_index(
            [("tenant", 1)],
            name="org_settings_tenant_index",
            unique=True,
            background=True,
        )

    async def create_task_schema_indices(self):
        await self._task_schemas_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1)],
            name="task_schema_tenant_index",
            unique=True,
            background=True,
        )

    async def create_task_evaluators_indices(self):
        await self._task_evaluators_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1), ("evaluator_type", 1), ("active", 1)],
            name="default_with_deleted",
            background=True,
        )

    async def create_task_benchmarks_indices(self):
        await self._task_benchmarks_collection.create_index(
            [("task_id", 1), ("task_schema_id", 1), ("by_input.task_input_hash", 1)],
            name="task_benchmarks_task_input_hash_index",
            background=True,
        )

        await self._task_benchmarks_collection.create_index(
            [("task_id", 1), ("task_schema_id", 1), ("by_input.by_group.task_group_iteration", 1)],
            name="task_benchmarks_task_group_iteration_index",
            background=True,
        )

        await self._task_benchmarks_collection.create_index(
            [
                ("task_id", 1),
                ("task_schema_id", 1),
                ("by_input.by_group.scores.example_id", 1),
                ("by_input.by_group.scores.evaluator_name", 1),
            ],
            name="scores",
            background=True,
        )

    async def create_task_indices(self):
        await self._tasks_collection.create_index(
            [("tenant", 1), ("task_id", 1)],
            name="task_id",
            unique=True,
            background=True,
        )

    async def create_task_input_indices(self):
        await self._task_inputs_collection.create_index(
            [("tenant", 1), ("task.id", 1), ("task.schema_id", 1), ("task_input_hash", 1)],
            name="default",
            unique=True,
            background=True,
        )

    async def create_task_images_indices(self):
        await self._task_images_collection.create_index(
            [("tenant", 1), ("task_id", 1)],
            name="task_images_tenant_task_id_index",
            unique=True,
            background=True,
        )

    async def apply(self) -> None:
        await self.create_task_variants_indices()
        await self.create_task_schema_id_indices()

        await self.create_task_run_group_indices()
        await self.create_task_run_group_idx_indices()

        await self.create_task_run_indices()
        await self.create_org_settings_indices()

        await self.create_task_schema_indices()
        await self.create_task_evaluators_indices()

        await self.create_task_benchmarks_indices()

        await self.create_task_indices()
        await self.create_task_input_indices()
        await self.create_task_images_indices()

    async def rollback(self) -> None:
        pass
