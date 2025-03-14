import pytest

from core.domain.field_based_evaluation_config import FieldBasedEvaluationConfig, StringComparisonOptions
from core.domain.task_evaluator import (
    CodeEvaluator,
    EvaluatorType,
    FaithfulnessEvaluator,
    FieldBasedEvaluator,
    TaskBasedEvaluator,
    TaskEvaluator,
)
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.storage.mongo.models.task_evaluator import TaskEvaluatorDocument


@pytest.mark.parametrize(
    "evaluator_type",
    [
        TaskBasedEvaluator(
            type="evaluate_output",
            task_id="task_id",
            task_schema_id=1,
            task_group=TaskGroup(
                iteration=1,
                id="id",
                properties=TaskGroupProperties(temperature=1),
                tags=["h"],
            ),
        ),
        TaskBasedEvaluator(
            type="compare_outputs",
            task_id="task_id",
            task_schema_id=1,
            task_group=TaskGroup(
                iteration=1,
                id="id",
                properties=TaskGroupProperties(temperature=1),
                tags=["h"],
            ),
        ),
        CodeEvaluator(python_code="print('hello')"),
        FieldBasedEvaluator(config=FieldBasedEvaluationConfig(options=StringComparisonOptions())),
        FaithfulnessEvaluator(new_user_message_keypath=["user"], new_assistant_answer_keypath=["assistant"]),
    ],
)
def test_domain_sanity(evaluator_type: EvaluatorType):
    evaluator = TaskEvaluator(id="664ba7f989c421635a026b8a", name="2", evaluator_type=evaluator_type)

    schema = TaskEvaluatorDocument.from_domain(
        evaluator=evaluator,
        tenant="tenant",
        task_id="task_id",
        task_schema_id=1,
    )
    assert schema.to_domain() == evaluator
