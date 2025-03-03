from typing import Any, Optional, Self, cast

from pydantic import BaseModel, Field

from core.domain.field_based_evaluation_config import FieldBasedEvaluationConfig
from core.domain.task_evaluation import EvaluatorMetric
from core.domain.task_evaluator import (
    CodeEvaluator,
    EvaluatorTrigger,
    EvaluatorType,
    EvalV2Evaluator,
    FaithfulnessEvaluator,
    FieldBasedEvaluator,
    TaskBasedEvaluator,
    TaskEvaluator,
)
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.models.run_identifier import RunOrUserIdentifier


class TaskEvaluatorDocument(BaseDocumentWithID):
    """An evaluator that will compare the run output with the output of an associated example using an LLM"""

    name: str

    metric: str

    triggers: list[str]

    task_id: str = Field(description="The task id this evaluator is associated with")

    task_schema_id: int = Field(description="The task schema id this evaluator is associated with")

    uses_examples: bool

    evaluator_type: str

    properties: "Properties"

    active: bool = True

    is_loading: bool | None = None

    class Properties(BaseModel):
        evaluator_task_id: Optional[str] = None
        evaluator_task_schema_id: Optional[int] = None

        class Group(BaseModel):
            iteration: int
            id: str
            properties: dict[str, Any]
            tags: list[str]

        evaluator_task_group: Optional[Group] = None

        python_code: Optional[str] = None

        field_config: Optional[dict[str, Any]] = None

        new_user_message_keypath: list[str | int] | None = None

        new_assistant_answer_keypath: list[str | int] | None = None

        instructions: Optional[str] = None

        instructions_updated_by: RunOrUserIdentifier | None = None

        @classmethod
        def from_domain(cls, evaluator_type: EvaluatorType) -> Self:
            match evaluator_type:
                case TaskBasedEvaluator():
                    return cls(
                        evaluator_task_id=evaluator_type.task_id,
                        evaluator_task_schema_id=evaluator_type.task_schema_id,
                        evaluator_task_group=cls.Group(
                            iteration=evaluator_type.task_group.iteration,
                            id=evaluator_type.task_group.id,
                            properties=evaluator_type.task_group.properties.model_dump(exclude_none=True),
                            tags=evaluator_type.task_group.tags,
                        ),
                    )
                case CodeEvaluator():
                    return cls(python_code=evaluator_type.python_code)
                case FieldBasedEvaluator():
                    return cls(field_config=evaluator_type.config.model_dump(exclude_none=True))
                case FaithfulnessEvaluator():
                    return cls(
                        new_user_message_keypath=evaluator_type.new_user_message_keypath,
                        new_assistant_answer_keypath=evaluator_type.new_assistant_answer_keypath,
                    )
                case EvalV2Evaluator():
                    return cls(
                        instructions=evaluator_type.instructions,
                        instructions_updated_by=RunOrUserIdentifier.from_domain(evaluator_type.instructions_updated_by)
                        if evaluator_type.instructions_updated_by
                        else None,
                    )
            raise ValueError(f"Unknown evaluator type {evaluator_type}")

        def to_domain(self, type: str, metric: EvaluatorMetric) -> EvaluatorType:
            match type:
                case "evaluate_output" | "compare_outputs":
                    if not self.evaluator_task_id or not self.evaluator_task_schema_id or not self.evaluator_task_group:
                        raise ValueError("TaskBasedEvaluator properties are missing")
                    return TaskBasedEvaluator(
                        type=type,
                        task_id=self.evaluator_task_id,
                        task_schema_id=self.evaluator_task_schema_id,
                        task_group=TaskGroup(
                            iteration=self.evaluator_task_group.iteration,
                            id=self.evaluator_task_group.id,
                            properties=TaskGroupProperties.model_validate(self.evaluator_task_group.properties),
                            tags=self.evaluator_task_group.tags,
                        ),
                    )
                case "code_compare_outputs":
                    if not self.python_code:
                        raise ValueError("CodeEvaluator properties are missing")
                    return CodeEvaluator(python_code=self.python_code)
                case "field_based":
                    if not self.field_config:
                        raise ValueError("FieldBasedEvaluator properties are missing")
                    return FieldBasedEvaluator(config=FieldBasedEvaluationConfig.model_validate(self.field_config))
                case "faithfulness":
                    # since the min len is 1, a validation error will be thrown if the keypaths are missing
                    return FaithfulnessEvaluator(
                        new_user_message_keypath=self.new_user_message_keypath or [],
                        new_assistant_answer_keypath=self.new_assistant_answer_keypath or [],
                    )
                case "evalv2":
                    return EvalV2Evaluator(
                        instructions=self.instructions or "",
                        instructions_updated_by=self.instructions_updated_by.to_domain()
                        if self.instructions_updated_by
                        else None,
                    )
                case _:
                    raise ValueError(f"Unknown evaluator type {type}")

    @classmethod
    def from_domain(cls, tenant: str, task_id: str, task_schema_id: int, evaluator: TaskEvaluator) -> Self:
        return cls(
            _id=PyObjectID.from_str(evaluator.id),
            task_id=task_id,
            task_schema_id=task_schema_id,
            tenant=tenant,
            name=evaluator.name,
            metric=evaluator.metric,
            triggers=[str(t) for t in evaluator.triggers],
            uses_examples=evaluator.evaluator_type.uses_examples,
            evaluator_type=evaluator.evaluator_type.type,
            properties=cls.Properties.from_domain(evaluator.evaluator_type),
            is_loading=evaluator.is_loading,
            active=evaluator.active,
        )

    def to_domain(self) -> TaskEvaluator:
        return TaskEvaluator(
            id=str(self.id) if self.id else "",
            name=self.name,
            triggers={cast(EvaluatorTrigger, t) for t in self.triggers},
            evaluator_type=self.properties.to_domain(self.evaluator_type, metric=cast(EvaluatorMetric, self.metric)),
            active=self.active,
            is_loading=self.is_loading or False,
        )
