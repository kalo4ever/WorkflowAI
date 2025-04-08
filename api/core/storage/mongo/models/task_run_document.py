import logging
from datetime import datetime, timedelta
from typing import Any, Literal, Optional, Self

from pydantic import BaseModel, Field, model_validator

from core.domain.consts import METADATA_KEY_PROVIDER_NAME, METADATA_KEY_USED_PROVIDERS
from core.domain.error_response import ErrorResponse
from core.domain.fields.internal_reasoning_steps import InternalReasoningStep
from core.domain.llm_completion import LLMCompletion as DLLMCompletion
from core.domain.llm_usage import LLMUsage
from core.domain.models import Provider
from core.domain.search_query import SearchQuery
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_run import Run, RunBase
from core.domain.task_run_query import SerializableTaskRunField, SerializableTaskRunQuery
from core.domain.utils import compute_eval_hash
from core.storage.mongo.models.tool_call_schema import ToolCallResultSchema, ToolCallSchema
from core.utils.fields import datetime_factory
from core.utils.iter_utils import safe_map_optional

from ..utils import (
    projection,
    query_set_filter,
)
from .base_document import BaseDocumentWithStrID
from .task_metadata import TaskMetadataSchema
from .task_query import build_task_query_filter

logger = logging.getLogger(__name__)


class TaskRunDocument(BaseDocumentWithStrID):
    """A task run represents an instance of a task being executed"""

    created_at: datetime = Field(default_factory=datetime_factory)

    duration_seconds: Optional[float] = None
    cost_usd: Optional[float] = None

    task: TaskMetadataSchema | None = None

    task_input_hash: str = ""
    task_input_preview: str = ""
    task_input: dict[str, Any] = {}

    task_output_hash: str = ""
    task_output_preview: str = ""
    task_output: dict[str, Any] = {}

    class Group(BaseModel):
        alias: str = ""
        hash: str = ""
        iteration: int = 0
        properties: dict[str, Any] | None = None
        tags: list[str] | None = None

    group: Group | None = None

    metadata: dict[str, Any] | None = None

    author_tenant: str | None = None

    # Is external is only stored, not exposed to the API for now
    is_external: bool | None = None

    class LLMCompletion(BaseModel):
        duration_seconds: Optional[float] = None
        messages: Optional[list[dict[str, Any]]] = None
        response: Optional[str] = None
        tool_calls: list[ToolCallSchema] | None = None

        usage: Optional[LLMUsage] = None
        provider: Optional[Provider] = None

        config_id: Optional[str] = None
        preserve_credits: Optional[bool] = None

        def to_domain(self, default_provider: Provider) -> DLLMCompletion:
            return DLLMCompletion(
                duration_seconds=self.duration_seconds,
                messages=self.messages or [],
                response=self.response,
                tool_calls=safe_map_optional(self.tool_calls, ToolCallSchema.to_domain, logger=logger),
                usage=self.usage or LLMUsage(),
                provider=self.provider or default_provider,
                config_id=self.config_id,
                preserve_credits=self.preserve_credits,
            )

        @classmethod
        def from_domain(cls, llm_completion: DLLMCompletion) -> Self:
            return cls(
                duration_seconds=llm_completion.duration_seconds,
                messages=llm_completion.messages,
                response=llm_completion.response,
                usage=llm_completion.usage,
                tool_calls=safe_map_optional(llm_completion.tool_calls, ToolCallSchema.from_domain, logger=logger),
                config_id=llm_completion.config_id,
                preserve_credits=llm_completion.preserve_credits,
            )

    llm_completions: Optional[list[LLMCompletion]] = Field(
        default=None,
        description="A list of raw completions used to generate the task output",
    )

    # List of executed tools
    tool_calls: list[ToolCallResultSchema] | None = None

    # List of function calls
    tool_call_requests: list[ToolCallSchema] | None = None

    config_id: Optional[str] = None

    status: Literal["success", "failure"] = "success"

    private_fields: list[str] | None = None

    is_active: bool | None = None

    eval_hash: str | None = None

    class ReasoningStep(BaseModel):
        title: str | None = None
        step: str | None = None
        output: str | None = None

        def to_domain(self) -> InternalReasoningStep:
            return InternalReasoningStep(title=self.title, explaination=self.step or "", output=self.output)

        @classmethod
        def from_domain(cls, reasoning_step: InternalReasoningStep) -> Self:
            return cls(title=reasoning_step.title, step=reasoning_step.explaination, output=reasoning_step.output)

    reasoning_steps: list[ReasoningStep] | None = None

    class Error(BaseModel):
        details: dict[str, Any] | None = None
        message: str = ""
        status_code: int = 0
        code: str = "internal_error"

        @classmethod
        def from_domain(cls, error: ErrorResponse.Error) -> Self:
            return cls(
                details=error.details,
                message=error.message,
                status_code=error.status_code,
                code=error.code,
            )

        def to_domain(self) -> ErrorResponse.Error:
            return ErrorResponse.Error(
                details=self.details,
                message=self.message,
                status_code=self.status_code,
                code=self.code,  # pyright: ignore[reportArgumentType]
            )

    error: Error | None = None

    @classmethod
    def from_resource(cls, task_run: Run) -> Self:
        return cls(
            _id=task_run.id,
            created_at=task_run.created_at,
            duration_seconds=task_run.duration_seconds,
            cost_usd=task_run.cost_usd,
            task=TaskMetadataSchema(
                id=task_run.task_id,
                schema_id=task_run.task_schema_id,
            ),
            task_input_hash=task_run.task_input_hash,
            task_input=task_run.task_input,
            task_input_preview=task_run.task_input_preview,
            task_output_hash=task_run.task_output_hash,
            task_output=task_run.task_output,
            task_output_preview=task_run.task_output_preview,
            group=cls.Group(
                alias=task_run.group.id or "",
                hash=task_run.group.id,
                iteration=task_run.group.iteration,
                properties=task_run.group.properties.model_dump(exclude_none=True),
                tags=task_run.group.tags or [],
            ),
            llm_completions=safe_map_optional(
                task_run.llm_completions,
                cls.LLMCompletion.from_domain,
                logger=logger,
            ),
            tool_calls=safe_map_optional(task_run.tool_calls, ToolCallResultSchema.from_domain, logger=logger),
            tool_call_requests=safe_map_optional(
                task_run.tool_call_requests,
                ToolCallSchema.from_domain,
                logger=logger,
            ),
            metadata=task_run.metadata,
            status=task_run.status,
            error=cls.Error.from_domain(task_run.error) if task_run.error else None,
            author_tenant=task_run.author_tenant,
            is_external=task_run.is_external,
            private_fields=list(task_run.private_fields) if task_run.private_fields else None,
            is_active=task_run.is_active,
            reasoning_steps=safe_map_optional(task_run.reasoning_steps, cls.ReasoningStep.from_domain, logger=logger),
            eval_hash=task_run.eval_hash,
        )

    def to_base(self) -> RunBase:
        return RunBase(
            id=self.id,
            created_at=self.created_at,
            duration_seconds=self.duration_seconds,
            cost_usd=self.cost_usd,
            task_id=self.task.id if self.task else "",
            task_schema_id=self.task.schema_id if self.task else 0,
            task_input_hash=self.task_input_hash,
            task_input_preview=self.task_input_preview,
            task_output_hash=self.task_output_hash,
            task_output_preview=self.task_output_preview,
            group=TaskGroup(
                id=self.group.alias or self.group.hash,
                iteration=self.group.iteration,
                properties=TaskGroupProperties.model_validate(self.group.properties)
                if self.group.properties
                else TaskGroupProperties(),
                tags=self.group.tags or [],
                schema_id=self.task.schema_id if self.task else 0,
            )
            if self.group
            else TaskGroup(),
            status=self.status,
            error=self.error.to_domain() if self.error else None,
            author_tenant=self.author_tenant,
            eval_hash=self.eval_hash or "",
        )

    def to_resource(self) -> Run:
        run = Run(
            id=self.id,
            created_at=self.created_at,
            duration_seconds=self.duration_seconds,
            cost_usd=self.cost_usd,
            task_id=self.task.id if self.task else "",
            task_schema_id=self.task.schema_id if self.task else 0,
            task_input=self.task_input,
            task_input_hash=self.task_input_hash,
            task_input_preview=self.task_input_preview,
            task_output=self.task_output,
            task_output_hash=self.task_output_hash,
            task_output_preview=self.task_output_preview,
            group=TaskGroup(
                id=self.group.alias or self.group.hash,
                iteration=self.group.iteration,
                properties=TaskGroupProperties.model_validate(self.group.properties)
                if self.group.properties
                else TaskGroupProperties(),
                tags=self.group.tags or [],
                schema_id=self.task.schema_id if self.task else 0,
            )
            if self.group
            else TaskGroup(),
            tool_calls=safe_map_optional(self.tool_calls, ToolCallResultSchema.to_domain, logger=logger),
            tool_call_requests=safe_map_optional(self.tool_call_requests, ToolCallSchema.to_domain, logger=logger),
            metadata=self.metadata,
            status=self.status,
            error=self.error.to_domain() if self.error else None,
            author_tenant=self.author_tenant,
            private_fields=set(self.private_fields) if self.private_fields else None,
            is_active=self.is_active,
            reasoning_steps=safe_map_optional(self.reasoning_steps, self.ReasoningStep.to_domain, logger=logger),
            eval_hash=self.eval_hash or "",
        )

        if self.llm_completions:
            completions: list[DLLMCompletion] = []
            for idx, item in enumerate(self.llm_completions):
                # Compatibility layer for deprecated data
                if item.provider:
                    continue
                try:
                    provider = _get_provider_for_run(run, idx)
                    if not provider:
                        raise ValueError(f"No provider found for run {run.id}")
                    completions.append(item.to_domain(Provider(provider)))
                except Exception as e:
                    if logger:
                        logger.exception(e)
            run.llm_completions = completions
        return run

    @classmethod
    def build_filter(cls, tenant: str, query: SerializableTaskRunQuery) -> dict[str, Any]:  # noqa: C901
        filter = build_task_query_filter(tenant, query)

        if query.status:
            filter["status"] = query.status

        if query.task_input_hashes:
            filter["task_input_hash"] = query_set_filter(query.task_input_hashes, True)
        if query.task_output_hash:
            filter["task_output_hash"] = query.task_output_hash

        if query.group_ids:
            filter["group.hash"] = query_set_filter(query.group_ids, True)

        if query.created_after and query.created_before:
            filter["created_at"] = {"$gt": query.created_after, "$lte": query.created_before}
        elif query.created_after:
            filter["created_at"] = {"$gt": query.created_after, "$lte": datetime.now() + timedelta(days=1)}
        elif query.created_before:
            filter["created_at"] = {"$gt": datetime.min, "$lte": query.created_before}

        if query.status:
            filter["status"] = query_set_filter(query.status, True)

        if query.is_active is not None:
            filter["is_active"] = query.is_active

        if query.metadata:
            for key, value in query.metadata.items():
                filter[f"metadata.{key}"] = value

        return filter

    @classmethod
    def build_project(
        cls,
        include: set[SerializableTaskRunField] | None,
        exclude: set[SerializableTaskRunField] | None,
    ) -> dict[str, Any] | None:
        if include is None and exclude is None:
            # By default, exclude tool calls and LLM completions
            exclude = {"tool_calls", "tool_call_requests", "llm_completions"}
        return projection(
            include=include,
            exclude=exclude,
            mapping={"task_schema_id": "task.schema_id", "version_id": "group.hash"},
        )

    @classmethod
    def build_sort(cls, query: SerializableTaskRunQuery) -> tuple[str, int] | None:
        return ("created_at", -1)

    # @classmethod
    # def _build_array_length_filter(cls, search_field: FieldQuery) -> dict[str, Any]:
    #     field_path = f"${search_field.field_name}"
    #     value = int(search_field.values[0])

    #     match search_field.operator:
    #         case SearchOperator.IS:
    #             return {"$size": value}
    #         case _:
    #             comparison = {
    #                 SearchOperator.IS_NOT: "$ne",
    #                 SearchOperator.GREATER_THAN: "$gt",
    #                 SearchOperator.GREATER_THAN_OR_EQUAL_TO: "$gte",
    #                 SearchOperator.LESS_THAN: "$lt",
    #                 SearchOperator.LESS_THAN_OR_EQUAL_TO: "$lte",
    #             }[search_field.operator]

    #             return {
    #                 "$expr": {
    #                     "$cond": {
    #                         "if": {"$eq": [{"$type": field_path}, "array"]},
    #                         "then": {comparison: [{"$size": field_path}, value]},
    #                         "else": False,
    #                     },
    #                 },
    #             }

    # @classmethod
    # def _doc_field_from_query(cls, query_field: SearchQuery) -> str:
    #     match query_field.field:
    #         case SearchField.SCHEMA_ID:
    #             return "task.schema_id"
    #         case SearchField.TIME:
    #             return "created_at"
    #         case SearchField.STATUS:
    #             return "status"
    #         case SearchField.REVIEW:
    #             return "final_review"
    #         case SearchField.MODEL:
    #             return "group.properties.model"
    #         case SearchField.TEMPERATURE:
    #             return "group.properties.temperature"
    #         case SearchField.PRICE:
    #             return "cost_usd"
    #         case SearchField.LATENCY:
    #             return "duration_seconds"
    #         case SearchField.SOURCE:
    #             return "is_active"
    #         case SearchField.INPUT:
    #             return f"task_input.{query_field.key_path}"
    #         case SearchField.OUTPUT:
    #             return f"task_output.{query_field.key_path}"
    #         case _:
    #             raise ValueError(f"Unsupported field: {query_field.field}")

    # @classmethod
    # def _build_field_filter(cls, search_field: SearchQuery) -> dict[str, Any]:  # noqa: C901
    #     if search_field.field == SearchField.METADATA:
    #         if not isinstance(search_field.operation, SearchOperationSingle):
    #             raise BadRequestError("Metadata field does not support the given operation")

    #         # Fields with nested keys with "." need to be handled differently
    #         if "." in search_field.key_path:
    #             get_field = {"$getField": {"field": search_field.key_path, "input": "$metadata"}}
    #             match search_field.operator:
    #                 case SearchOperator.IS:
    #                     return {
    #                         "$expr": {
    #                             "$and": [
    #                                 {"$ne": [get_field, None]},
    #                                 {"$eq": [get_field, search_field.operation.value]},
    #                             ],
    #                         },
    #                     }
    #                 case SearchOperator.IS_NOT:
    #                     return {
    #                         "$expr": {
    #                             "$or": [
    #                                 {"$eq": [get_field, None]},
    #                                 {"$ne": [get_field, search_field.operation.value]},
    #                             ],
    #                         },
    #                     }
    #                 case _:
    #                     raise ValueError(f"Unsupported operator for metadata field: {search_field.operator}")

    #     if search_field.field_type == "array_length":
    #         if not isinstance(search_field.operation, SearchOperationSingle):
    #             raise BadRequestError("Array length field does not support the given operation")

    #         return array_length_filter(
    #             operator=search_field.operation.operator,
    #             key=search_field.field[:-7],
    #             value=int(search_field.operation.value),
    #         )

    #     # If field exists in filter and is a dict, update existing conditions
    #     # TODO: Conflict possible with fields that have ".length" in their name that are not array lengths
    #     # We could check for field type here
    #     if search_field.field_name.endswith(".length"):
    #         return array_length_filter(
    #             operator=search_field.operator,
    #             key=search_field.field_name[:-7],
    #             value=int(search_field.values[0]),
    #         )

    #     match search_field.operator:
    #         case SearchOperator.IS:
    #             if isinstance(search_field.values[0], str):
    #                 return _add_name({"$regex": f"^{search_field.values[0]}"})
    #             return _add_name({"$eq": search_field.values[0]})
    #         case SearchOperator.IS_NOT:
    #             if isinstance(search_field.values[0], str):
    #                 return _add_name({"$not": {"$regex": f"^{search_field.values[0]}$", "$options": "i"}})
    #             return _add_name({"$ne": search_field.values[0]})
    #         case SearchOperator.GREATER_THAN:
    #             return _add_name({"$gt": search_field.values[0]})
    #         case SearchOperator.GREATER_THAN_OR_EQUAL_TO:
    #             return _add_name({"$gte": search_field.values[0]})
    #         case SearchOperator.LESS_THAN:
    #             return _add_name({"$lt": search_field.values[0]})
    #         case SearchOperator.LESS_THAN_OR_EQUAL_TO:
    #             return _add_name({"$lte": search_field.values[0]})
    #         case SearchOperator.CONTAINS:
    #             return _add_name({"$regex": search_field.values[0], "$options": "i"})
    #         case SearchOperator.NOT_CONTAINS:
    #             return _add_name({"$not": {"$regex": search_field.values[0], "$options": "i"}})
    #         case SearchOperator.IS_BETWEEN:
    #             if len(search_field.values) < 2:
    #                 raise InternalError(
    #                     "BETWEEN operator requires two values",
    #                     extras={"search_field": search_field.model_dump()},
    #                 )
    #             return _add_name({"$gte": search_field.values[0], "$lte": search_field.values[1]})
    #         case SearchOperator.IS_NOT_BETWEEN:
    #             # TODO: Optimize the `is not between` operator so index can be used. OR is better for this
    #             if len(search_field.values) < 2:
    #                 raise InternalError(
    #                     "NOT_BETWEEN operator requires two values",
    #                     extras={"search_field": search_field.model_dump()},
    #                 )
    #             return _add_name({"$not": {"$gte": search_field.values[0], "$lte": search_field.values[1]}})
    #         case SearchOperator.IS_EMPTY:
    #             return is_empty_filter(search_field.type, search_field.field_name)
    #         case SearchOperator.IS_NOT_EMPTY:
    #             return is_not_empty_filter(search_field.type, search_field.field_name)
    #         case SearchOperator.IS_BEFORE:
    #             return _add_name({"$lt": search_field.values[0]})
    #         case SearchOperator.IS_AFTER:
    #             return _add_name({"$gte": search_field.values[0]})

    @classmethod
    def build_search_filter(
        cls,
        tenant: str,
        task_id: str,
        search_fields: list[SearchQuery] | None,
    ) -> dict[str, Any]:
        # TODO: re-enable search fields
        return {
            "tenant": tenant,
            "task.id": task_id,
        }
        # query, search_fields = SerializableTaskRunQuery.from_search_fields(task_id, search_fields)
        # filter = cls.build_filter(tenant, query)
        # if search_fields is None:
        #     return filter

        # for search_field in search_fields:
        #     new_filter = cls._build_field_filter(search_field)
        #     merge_filters(filter, new_filter)

        #     # Strip out any None fields for $and and $or
        # return {k: v for k, v in filter.items() if k not in ["$or", "$and"] or v is not None}

    @model_validator(mode="after")
    def compute_eval_hash(self):
        if self.eval_hash is None and self.task:
            self.eval_hash = compute_eval_hash(
                self.task.schema_id,
                self.task_input_hash,
                self.task_output_hash,
            )
        return self


def _get_provider_for_run(run: Run, completion_idx: int | None = None) -> str | None:
    if run.group.properties.provider is not None:
        return run.group.properties.provider

    if run.metadata is not None:
        if providers := run.metadata.get(METADATA_KEY_USED_PROVIDERS):
            if completion_idx is not None:
                try:
                    return providers[completion_idx]
                except IndexError:
                    pass
            return providers[-1]
        if provider := run.metadata.get(METADATA_KEY_PROVIDER_NAME):
            return provider

    return None
