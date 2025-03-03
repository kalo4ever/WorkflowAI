from typing import Annotated, Literal, Self, Union

from pydantic import BaseModel, Field, computed_field

from core.domain.field_based_evaluation_config import FieldBasedEvaluationConfig
from core.domain.run_identifier import RunIdentifier
from core.domain.task_evaluation import EvaluatorMetric
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.users import UserIdentifier

TaskEvaluatorTypeNames = Literal["evaluate_output", "compare_outputs"]

# TODO: add check for exhaustiveness
EvaluatorTypeName = TaskEvaluatorTypeNames | Literal["code_compare_outputs", "field_based", "faithfulness", "evalv2"]


class TaskBasedEvaluator(BaseModel):
    """An evaluator that will compare the run output with the output of an associated example using an LLM"""

    type: TaskEvaluatorTypeNames

    task_id: str = Field(description="The id of the evaluator task")
    task_schema_id: int = Field(description="The schema id of the evaluator task")
    task_group: TaskGroup = Field(description="The group that is used to run the evaluator task")

    metric: Literal[EvaluatorMetric] = "correctness"

    @computed_field(description="Whether the evaluator requires examples")
    @property
    def uses_examples(self) -> bool:
        return self.type == "compare_outputs"


class CodeEvaluator(BaseModel):
    """An evaluator that will compare the output of a run with the output of an associated example using code"""

    type: Literal["code_compare_outputs"] = "code_compare_outputs"
    python_code: str

    uses_examples: Literal[True] = True

    metric: Literal[EvaluatorMetric] = "correctness"


class FieldBasedEvaluator(BaseModel):
    """An evaluator that will compare the output of a run with the output of an
    associated example using field based comparisons"""

    type: Literal["field_based"] = "field_based"
    config: FieldBasedEvaluationConfig
    uses_examples: Literal[True] = True

    metric: Literal[EvaluatorMetric] = "correctness"


class FaithfulnessEvaluator(BaseModel):
    """An evaluator that computes the faithfulness of the assistant's answer to the user's message"""

    type: Literal["faithfulness"] = "faithfulness"

    new_user_message_keypath: list[str | int] = Field(
        description="A keypath to describe where to find the new user message in the task input",
        min_length=1,
    )
    new_assistant_answer_keypath: list[str | int] = Field(
        description="A keypath to describe where to find the new assistant answer in the task output",
        min_length=1,
    )

    faithfulness_task_group_properties: TaskGroupProperties | None = None

    uses_examples: Literal[True] = True

    metric: Literal[EvaluatorMetric] = "faithfulness"


class EvalV2Evaluator(BaseModel):
    type: Literal["evalv2"] = "evalv2"

    instructions: str

    instructions_updated_by: UserIdentifier | RunIdentifier | None = None

    metric: Literal[EvaluatorMetric] = "correctness"

    uses_examples: Literal[False] = False

    def is_similar_to(self, other: Self | None) -> bool:
        if not other:
            return not self.instructions
        return self.instructions == other.instructions


EvaluatorType = Annotated[
    Union[TaskBasedEvaluator, CodeEvaluator, FieldBasedEvaluator, FaithfulnessEvaluator, EvalV2Evaluator],
    Field(discriminator="type"),
]


EvaluatorTrigger = Literal["auto", "manual"]


class TaskEvaluator(BaseModel):
    id: str
    name: str

    is_loading: bool = False

    triggers: set[EvaluatorTrigger] = Field(
        default_factory=lambda: {"auto", "manual"},
        description="The triggers that will cause the evaluator to run",
    )

    evaluator_type: EvaluatorType

    active: bool = Field(default=True, description="Whether the evaluator is active")

    @computed_field
    @property
    def metric(self) -> EvaluatorMetric:
        return self.evaluator_type.metric

    @computed_field
    @property
    def type(self) -> EvaluatorTypeName:
        return self.evaluator_type.type

    @computed_field
    @property
    def uses_examples(self) -> bool:
        return self.evaluator_type.uses_examples
