import json
import logging
from typing import Any, AsyncIterator

from api.services.internal_tasks._internal_tasks_utils import (
    internal_tools_description,
)
from api.tasks.chat_task_schema_generation.apply_field_updates import (
    InputFieldUpdate,
    OutputFieldUpdate,
    apply_field_updates,
)
from api.tasks.improve_prompt import (
    ImprovePromptAgentInput,
    ImprovePromptAgentOutput,
    run_improve_prompt_agent,
)
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_io import SerializableTaskIO
from core.domain.task_variant import SerializableTaskVariant
from core.storage import TaskTuple
from core.storage.backend_storage import BackendStorage
from core.utils.models.dumps import safe_dump_pydantic_model
from core.utils.schema_sanitation import streamline_schema
from core.utils.schemas import strip_json_schema_metadata_keys


class ImprovePromptService:
    def __init__(self, storage: BackendStorage):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._storage = storage

    async def _prepare_improve_prompt_input(self, task_tuple: TaskTuple, run_id: str, user_evaluation: str):
        """Returns a tuple of ImprovePromptAgentInput, variant and baseline task group properties"""
        run = await self._storage.task_runs.fetch_task_run_resource(
            task_tuple,
            run_id,
            include={"version_id", "task_input", "task_output"},
        )
        version = await self._storage.task_groups.get_task_group_by_id(task_tuple[0], run.group.id)
        variant_id = version.properties.task_variant_id
        variant = await self._storage.task_version_resource_by_id(task_tuple[0], variant_id) if variant_id else None

        input_ = ImprovePromptAgentInput(
            original_agent_config=ImprovePromptAgentInput.AgentConfig(
                prompt=version.properties.instructions,
                input_schema=variant.input_schema.json_schema if variant else None,
                output_schema=variant.output_schema.json_schema if variant else None,
            ),
            agent_run=ImprovePromptAgentInput.AgentRun(
                run_input=json.dumps(run.task_input),
                run_output=json.dumps(run.task_output),
                user_evaluation=user_evaluation,
            ),
            available_tools_description=internal_tools_description(all=True),
        )
        return input_, variant, version.properties.model_dump(exclude_none=True)

    async def run(self, task_tuple: TaskTuple, run_id: str, user_evaluation: str):
        improve_prompt_input, variant, properties = await self._prepare_improve_prompt_input(
            task_tuple,
            run_id,
            user_evaluation,
        )
        res = await run_improve_prompt_agent(improve_prompt_input)
        updated_properties = {**properties, "instructions": res.improved_prompt}
        if created := await self._safe_handle_improved_output_schema(
            variant,
            res.input_field_updates,
            res.output_field_updates,
        ):
            updated_properties["task_variant_id"] = created
        return TaskGroupProperties.model_validate(updated_properties), res.changelog

    async def stream(
        self,
        task_tuple: TaskTuple,
        run_id: str,
        user_evaluation: str,
    ) -> AsyncIterator[tuple[TaskGroupProperties, list[str] | None]]:
        improve_prompt_input, variant, properties = await self._prepare_improve_prompt_input(
            task_tuple,
            run_id,
            user_evaluation,
        )

        chunk: ImprovePromptAgentOutput | None = None
        async for payload in run_improve_prompt_agent.stream(improve_prompt_input):
            chunk = payload.output
            yield (
                TaskGroupProperties.model_validate(
                    {**properties, "instructions": chunk.improved_prompt},
                ),
                chunk.changelog,
            )
        if chunk:
            if created_variant := await self._safe_handle_improved_output_schema(
                variant,
                chunk.input_field_updates,
                chunk.output_field_updates,
            ):
                # We yield one last time to include the new variant
                yield (
                    TaskGroupProperties.model_validate(
                        {
                            **properties,
                            "instructions": chunk.improved_prompt,
                            "task_variant_id": created_variant,
                        },
                    ),
                    chunk.changelog,
                )

    async def _safe_handle_improved_output_schema(
        self,
        task_variant: SerializableTaskVariant | None,
        input_field_updates: list[InputFieldUpdate] | None,
        output_field_updates: list[OutputFieldUpdate] | None,
    ):
        if not task_variant:
            return None

        try:
            return await self._handle_improved_output_schema(task_variant, input_field_updates, output_field_updates)
        except Exception as e:
            self._logger.exception(
                "Error handling improved output schema",
                exc_info=e,
                extra={
                    "output_schema": task_variant.output_schema.json_schema,
                    "input_field_updates": safe_dump_pydantic_model(input_field_updates),
                    "output_field_updates": safe_dump_pydantic_model(output_field_updates),
                },
            )
            return None

    def _schema_with_updates(
        self,
        schema: dict[str, Any],
        updates: list[InputFieldUpdate] | list[OutputFieldUpdate],
    ) -> dict[str, Any]:
        if not updates:
            return schema

        computed = streamline_schema(apply_field_updates(schema, updates))
        # Removing examples from non string or enum fields
        # TODO: is that actually desired ? we might have weird cases where
        # the changelog is different from what actually happned
        return strip_json_schema_metadata_keys(
            computed,
            {"examples"},
            filter=lambda d: d.get("type") != "string" or "enum" in d,
        )

    async def _handle_improved_output_schema(
        self,
        task_variant: SerializableTaskVariant,
        input_field_updates: list[InputFieldUpdate] | None,
        output_field_updates: list[OutputFieldUpdate] | None,
    ):
        # No update to apply, early return
        if not input_field_updates and not output_field_updates:
            return None

        input_schema = (
            self._schema_with_updates(task_variant.input_schema.json_schema, input_field_updates)
            if input_field_updates is not None
            else task_variant.input_schema.json_schema
        )

        output_schema = (
            self._schema_with_updates(task_variant.output_schema.json_schema, output_field_updates)
            if output_field_updates is not None
            else task_variant.output_schema.json_schema
        )

        # Store the new task variant
        new_task_variant = SerializableTaskVariant(
            id="",
            task_id=task_variant.task_id,
            task_schema_id=0,
            name="",
            input_schema=SerializableTaskIO.from_json_schema(input_schema),
            output_schema=SerializableTaskIO.from_json_schema(output_schema),
        )
        created, _ = await self._storage.store_task_resource(new_task_variant)
        return created.id
