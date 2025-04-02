from collections.abc import Coroutine
from datetime import datetime, time
from typing import Any, Callable, Generator, Optional
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, Field

from core.agents.text_equivalence_task import TextEquivalenceTaskOutput
from core.deprecated.workflowai import WorkflowAI
from core.domain.field_based_evaluation_config import (
    ArrayComparisonOptions,
    FieldBasedEvaluationConfig,
    NumberComparisonOptions,
    ObjectComparisonOptions,
    StringComparisonOptions,
)
from core.evaluators.field_based_compare import EvaluationError, FieldBasedCompare
from core.utils.schemas import JsonSchema
from tests.models import task_example_ser, task_run_ser, task_variant
from tests.utils import fixtures_json


class Item(BaseModel):
    name1: str = Field(..., description="The name of the item", examples=["Widget"])
    description: str = Field(..., description="A detailed description of the item", examples=["A useful tool for X"])
    opt_description: Optional[str] = None
    opt_description2: str | None = None
    price: float = Field(..., description="The price of the item in dollars", examples=[12.99])
    in_stock: bool = Field(..., description="Whether the item is in stock")

    class Sub1(BaseModel):
        key1: str
        key2: int = Field(..., description="Value in cents")

    sub1: Sub1 = Field(..., description="A submodel")

    class Sub2(BaseModel):
        key3: Optional[str] = Field(..., description="Some key3")

    sub2: list[Sub2] = Field(..., description="a list of submodels")

    string_array: list[str] = Field(..., description="A list of strings")

    ignored: str = ""
    datetime_field: datetime = datetime(2021, 1, 1)

    time_field: time = Field(
        description="The time of the local datetime without timezone info.",
        examples=["12:00:00", "22:00:00"],
        json_schema_extra={"format": "time"},
    )

    class Nested(BaseModel):
        nested_string: str
        nested_number: float
        nested_bool: bool

    nested: Nested


@pytest.fixture(scope="function")
def item() -> Item:
    return Item(
        name1="Widget",
        description="A useful tool for X",
        price=12.99,
        in_stock=True,
        sub1=Item.Sub1(key1="1", key2=1),
        sub2=[Item.Sub2(key3="1")],
        string_array=["a", "b"],
        time_field=time(12, 0, 0),
        nested=Item.Nested(nested_string="nested_string", nested_number=1.0, nested_bool=False),
    )


@pytest.fixture(scope="function")
def item2(item: Item) -> Item:
    return item.model_copy(deep=True)


@pytest.fixture(scope="function")
def config() -> FieldBasedEvaluationConfig:
    return FieldBasedEvaluationConfig(
        options=ObjectComparisonOptions(
            property_evaluations={
                "name1": StringComparisonOptions(),
                "description": StringComparisonOptions(semantics=True),
                "opt_description": StringComparisonOptions(strict_equality=True),
                "price": NumberComparisonOptions(),
                "sub1": ObjectComparisonOptions(
                    property_evaluations={
                        "key2": NumberComparisonOptions(delta=1),
                    },
                ),
                "string_array": ArrayComparisonOptions(
                    ignore_order=True,
                    element_evaluation=StringComparisonOptions(
                        case_sensitive=False,
                    ),
                ),
                "sub2": ArrayComparisonOptions(
                    ignore_order=True,
                ),
                "time": StringComparisonOptions(strict_equality=True),
                "ignored": StringComparisonOptions(ignore=True),
            },
        ),
    )


CompareFn = Callable[[Item, Item], Coroutine[Any, Any, list[EvaluationError]]]


@pytest.fixture(scope="function")
def evaluator(config: FieldBasedEvaluationConfig):
    return FieldBasedCompare(
        task_variant(output_schema=Item.model_json_schema()),  # noqa: F821
        config=config,
        name="test_name",
        id="test_id",
    )


@pytest.fixture(scope="function")
def compare(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig) -> CompareFn:
    async def compare_fn(item1: Item, item2: Item) -> list[EvaluationError]:
        return await evaluator.compare(
            item1.model_dump(mode="json"),
            item2.model_dump(mode="json"),
            config.options,
            evaluator._output_schema(),  # pyright: ignore [reportPrivateUsage]
        )

    return compare_fn


@pytest.fixture(scope="function")
def wai() -> Generator[AsyncMock, None, None]:
    mockwai = AsyncMock()
    with mock.patch.object(WorkflowAI, "from_ctx", return_value=mockwai):
        yield mockwai


async def test_evaluator_compare_true(compare: CompareFn, item: Item) -> None:
    errors = await compare(item, item)
    assert len(errors) == 0


async def test_evaluator_compare_array_diff(compare: CompareFn, item: Item, item2: Item) -> None:
    item2.string_array = ["2"]
    assert len(item.string_array) == 2, "sanity"

    errors = await compare(item, item2)
    assert len(errors) == 1
    assert errors[0].keypath == "string_array"
    assert str(errors[0]) == "Difference at string_array: Lists have different lengths (got 1 expected 2)"


async def test_evaluator_compare_fuzzy_true(compare: CompareFn, item: Item, item2: Item, wai: AsyncMock) -> None:
    item2.description = "A useful tool for Y"

    wai.run.return_value = MagicMock(
        task_output=TextEquivalenceTaskOutput(are_texts_functionally_equivalent=True, reason_not_equivalent=""),
    )

    errors = await compare(item, item2)
    assert len(errors) == 0
    wai.run.assert_called_once()
    assert wai.run.call_args.kwargs["input"].correct_text == "A useful tool for X"
    assert wai.run.call_args.kwargs["input"].candidate_text == "A useful tool for Y"
    assert wai.run.call_args.kwargs["group"].properties.model == "gemini-1.5-pro-001"


async def test_evaluator_compare_fuzzy_false(compare: CompareFn, item: Item, item2: Item, wai: AsyncMock) -> None:
    item2.description = "Bogus"

    wai.run.return_value = TextEquivalenceTaskOutput(
        are_texts_functionally_equivalent=False,
        reason_not_equivalent="Some reason",
    )

    errors = await compare(item, item2)
    assert len(errors) == 1
    assert errors[0].keypath == "description"
    assert (
        str(errors[0])
        == "Difference at description: Semantics did not match between 'A useful tool for X' and 'Bogus': Some reason"
    )
    wai.run.assert_called_once()
    assert wai.run.call_args.kwargs["input"].correct_text == "A useful tool for X"
    assert wai.run.call_args.kwargs["input"].candidate_text == "Bogus"
    assert wai.run.call_args.kwargs["group"].properties.model == "gemini-1.5-pro-001"


async def test_evaluator_compare_strict(compare: CompareFn, item: Item, item2: Item, wai: AsyncMock) -> None:
    item.opt_description = "bla"
    item2.opt_description = "bla "  # add a whitespace

    errors = await compare(item, item2)
    assert len(errors) == 1
    assert errors[0].keypath == "opt_description"
    assert (
        str(errors[0]) == "Difference at opt_description: String values do not match. Compared 'bla ' to expected 'bla'"
    )


async def test_evaluator_soft_compare(compare: CompareFn, item: Item, item2: Item) -> None:
    item.name1 = "bla"
    item2.name1 = "BLÂ \n"

    errors = await compare(item, item2)
    assert len(errors) == 0


async def test_evaluator_ignored(compare: CompareFn, item: Item, item2: Item) -> None:
    item.ignored = "bla"
    del item2.ignored

    errors = await compare(item, item2)
    assert len(errors) == 0


async def test_evaluator_none(compare: CompareFn, item: Item, item2: Item) -> None:
    item.opt_description = "bla"
    item2.opt_description = None

    errors = await compare(item, item2)
    assert len(errors) == 1
    assert errors[0].keypath == "opt_description"
    assert str(errors[0]) == "Difference at opt_description: Expected 'bla' got null"


async def test_evaluator_multiple_errors(compare: CompareFn, item: Item, item2: Item) -> None:
    item.opt_description = "bla"
    item2.opt_description = None
    item.sub2 = [Item.Sub2(key3="1"), Item.Sub2(key3="3")]
    item2.sub2 = [Item.Sub2(key3="2"), Item.Sub2(key3="1")]

    errors = await compare(item, item2)
    assert len(errors) == 4
    assert errors[0].keypath == "opt_description"
    assert str(errors[0]) == "Difference at opt_description: Expected 'bla' got null"
    assert errors[1].keypath == "sub2"
    assert str(errors[1]) == "Difference at sub2: Could not find a list ordering that matches."
    assert errors[2].keypath == "sub2.0.key3"
    assert str(errors[2]) == "Difference at sub2.0.key3: String values do not match. Compared '2' to expected '1'"
    assert errors[3].keypath == "sub2.1.key3"
    assert str(errors[3]) == "Difference at sub2.1.key3: String values do not match. Compared '1' to expected '3'"


async def test_evaluator_multiple_errors_with_price(compare: CompareFn, item: Item, item2: Item) -> None:
    item.opt_description = "bla"
    item2.opt_description = None
    item.price = 12.99
    item2.price = 15.99
    item.sub2 = [Item.Sub2(key3="1"), Item.Sub2(key3="3")]
    item2.sub2 = [Item.Sub2(key3="1"), Item.Sub2(key3="1")]

    errors = await compare(item, item2)
    assert len(errors) == 4
    assert errors[0].keypath == "opt_description"
    assert str(errors[0]) == "Difference at opt_description: Expected 'bla' got null"
    assert errors[1].keypath == "price"
    assert str(errors[1]) == "Difference at price: Number values do not match. Got 15.99 expected 12.99"
    assert errors[2].keypath == "sub2"
    assert str(errors[2]) == "Difference at sub2: Could not find a list ordering that matches."
    assert errors[3].keypath == "sub2.1.key3"
    assert str(errors[3]) == "Difference at sub2.1.key3: String values do not match. Compared '1' to expected '3'"


async def test_evaluator_multiple_errors_with_name(compare: CompareFn, item: Item, item2: Item) -> None:
    item.name1 = "Widget"
    item2.name1 = "Gadget"
    item.opt_description = "bla"
    item2.opt_description = None

    errors = await compare(item, item2)
    assert len(errors) == 2
    assert errors[0].keypath == "name1"
    assert str(errors[0]) == "Difference at name1: String values do not match. Compared 'gadget' to expected 'widget'"
    assert errors[1].keypath == "opt_description"
    assert str(errors[1]) == "Difference at opt_description: Expected 'bla' got null"


async def test_evaluator_multiple_errors_with_in_stock(compare: CompareFn, item: Item, item2: Item) -> None:
    item.opt_description = "bla"
    item2.opt_description = None
    item.in_stock = True
    item2.in_stock = False
    item.nested.nested_string = "something"
    item2.nested.nested_string = "else"
    item.nested.nested_bool = True
    item2.nested.nested_bool = False

    errors = await compare(item, item2)
    assert len(errors) == 4

    assert errors[0].keypath == "opt_description"
    assert str(errors[0]) == "Difference at opt_description: Expected 'bla' got null"
    assert errors[1].keypath == "in_stock"
    assert str(errors[1]) == "Difference at in_stock: Bool values do not match. Got False expected True"
    assert errors[2].keypath == "nested.nested_string"
    assert (
        str(errors[2])
        == "Difference at nested.nested_string: String values do not match. Compared 'else' to expected 'something'"
    )
    assert errors[3].keypath == "nested.nested_bool"
    assert str(errors[3]) == "Difference at nested.nested_bool: Bool values do not match. Got False expected True"


async def test_evaluator_is_ignored(compare: CompareFn, item: Item, item2: Item) -> None:
    item2.ignored = "I am ignored"
    errors = await compare(item, item2)
    assert len(errors) == 0


async def test_basic_ignore_order(compare: CompareFn, item: Item, item2: Item) -> None:
    item2.string_array = ["B", "a"]  # item.string_array is ["a", "b"]
    errors = await compare(item, item2)
    assert len(errors) == 0


async def test_complex_ignore_order(compare: CompareFn, item: Item, item2: Item) -> None:
    item.sub2 = [Item.Sub2(key3="1"), Item.Sub2(key3="2")]
    item2.sub2 = [Item.Sub2(key3="2"), Item.Sub2(key3="1")]
    errors = await compare(item, item2)
    assert len(errors) == 0


async def test_complex_ignore_order_fail(compare: CompareFn, item: Item, item2: Item) -> None:
    item.sub2 = [Item.Sub2(key3="1"), Item.Sub2(key3="3")]
    item2.sub2 = [Item.Sub2(key3="2"), Item.Sub2(key3="1")]

    errors = await compare(item, item2)
    assert len(errors) == 3

    assert errors[0].keypath == "sub2"
    assert str(errors[0]) == "Difference at sub2: Could not find a list ordering that matches."

    assert errors[1].keypath == "sub2.0.key3"
    assert str(errors[1]) == "Difference at sub2.0.key3: String values do not match. Compared '2' to expected '1'"

    assert errors[2].keypath == "sub2.1.key3"
    assert str(errors[2]) == "Difference at sub2.1.key3: String values do not match. Compared '1' to expected '3'"


async def test_compare_float_ints(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig):
    item1 = {
        "price": 1.0,
    }
    item2 = {
        "price": 1,
    }

    errors = await evaluator.compare(item1, item2, config.options, evaluator._output_schema())  # pyright: ignore [reportPrivateUsage]
    assert len(errors) == 0


async def test_compare_invalid_types(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig):
    item1 = {
        "price": 1.0,
    }
    item2 = {
        "price": "1.0",
    }
    errors = await evaluator.compare(item1, item2, config.options, evaluator._output_schema())  # pyright: ignore [reportPrivateUsage]
    assert len(errors) == 1
    assert errors[0].keypath == "price"
    assert str(errors[0]) == "Difference at price: Types do not match. Got <str> expected <float>"


async def test_similar_time(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig):
    item1 = {"time_field": "22:00:00"}
    item2 = {"time_field": "22:00"}

    errors = await evaluator.compare(item1, item2, config.options, evaluator._output_schema())  # pyright: ignore [reportPrivateUsage]
    assert len(errors) == 0


async def test_same_time(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig):
    item1 = {"time_field": "22:00:00"}
    item2 = {"time_field": "22:00:00"}

    errors = await evaluator.compare(item1, item2, config.options, evaluator._output_schema())  # pyright: ignore [reportPrivateUsage]
    assert len(errors) == 0


async def test_different_time(evaluator: FieldBasedCompare, config: FieldBasedEvaluationConfig):
    item1 = {"time_field": "22:00:00"}
    item2 = {"time_field": "23:00:00"}

    errors = await evaluator.compare(item1, item2, config.options, evaluator._output_schema())  # pyright: ignore [reportPrivateUsage]
    assert len(errors) == 1
    assert errors[0].keypath == "time_field"
    assert str(errors[0]) == "Difference at time_field: Times do not match. Got 23:00:00 expected 22:00:00"


async def test_fixtures():
    output1 = fixtures_json("evals/output_1_cor.json")
    output1_exp = fixtures_json("evals/output_1_exp.json")
    output1_json_schema = fixtures_json("evals/output_1_json_schema.json")

    eval_config = FieldBasedEvaluationConfig.model_validate(fixtures_json("evals/output_1_eval_config.json"))

    evaluator = FieldBasedCompare(
        task=task_variant(output_schema=output1_json_schema),
        config=eval_config,
        name="test_name",
        id="test_id",
    )
    errors = await evaluator.compare(output1, output1_exp, eval_config.options, JsonSchema(output1_json_schema))
    assert len(errors) == 0


class TestEvaluateWithExample:
    async def test_evaluate_with_example_error(self, evaluator: FieldBasedCompare, item: Item, item2: Item):
        item.time_field = item.time_field.replace(hour=22)
        item2.time_field = item2.time_field.replace(hour=23)
        run = task_run_ser(task_output=item.model_dump(mode="json"), task_input=item.model_dump(mode="json"))
        example = task_example_ser(task_output=item2.model_dump(mode="json"), task_input=item.model_dump(mode="json"))

        evaluation = await evaluator.evaluate(run, example)
        assert evaluation.score == 0.0
        assert evaluation.evaluator.id == evaluator.definition.id

        assert evaluation.comment == "Difference at time_field: Times do not match. Got 22:00:00 expected 23:00:00"
        assert evaluation.model_dump()["error_details"] == [
            {
                "key_path": "time_field",
                "reason": "Difference at time_field: Times do not match. Got 22:00:00 expected 23:00:00",
            },
        ]
        assert len(evaluation.model_dump()["error_details"]) == 1

    async def test_evaluate_with_example_error_2(self, evaluator: FieldBasedCompare, item: Item, item2: Item):
        item.opt_description = "a"
        item2.opt_description = "b"
        run = task_run_ser(task_output=item.model_dump(mode="json"), task_input=item.model_dump(mode="json"))
        example = task_example_ser(task_output=item2.model_dump(mode="json"), task_input=item.model_dump(mode="json"))

        evaluation = await evaluator.evaluate(run, example)
        assert evaluation.score == 0.0
        assert evaluation.evaluator.id == evaluator.definition.id

        assert (
            evaluation.comment
            == "Difference at opt_description: String values do not match. Compared 'a' to expected 'b'"
        )
        assert evaluation.model_dump()["error_details"] == [
            {
                "key_path": "opt_description",
                "reason": "Difference at opt_description: String values do not match. Compared 'a' to expected 'b'",
            },
        ]
        assert len(evaluation.model_dump()["error_details"]) == 1

    async def test_evaluate_with_example_error_3(self, evaluator: FieldBasedCompare, item: Item, item2: Item):
        item.opt_description = "hello james !"
        item2.opt_description = "Hello James !"
        run = task_run_ser(task_output=item.model_dump(mode="json"), task_input=item.model_dump(mode="json"))
        example = task_example_ser(task_output=item2.model_dump(mode="json"), task_input=item.model_dump(mode="json"))

        evaluation = await evaluator.evaluate(run, example)
        assert evaluation.score == 0.0
        assert evaluation.evaluator.id == evaluator.definition.id

        assert (
            evaluation.comment
            == "Difference at opt_description: String values do not match. Compared 'hello james !' to expected 'Hello James !'"
        )
        assert evaluation.model_dump()["error_details"] == [
            {
                "key_path": "opt_description",
                "reason": "Difference at opt_description: String values do not match. Compared 'hello james !' to expected 'Hello James !'",
            },
        ]
        assert len(evaluation.model_dump()["error_details"]) == 1

    async def test_evaluate_with_example_OK(self, evaluator: FieldBasedCompare, item: Item, item2: Item):
        # item and item2 are equal
        run = task_run_ser(task_output=item.model_dump(mode="json"), task_input=item.model_dump(mode="json"))
        example = task_example_ser(task_output=item2.model_dump(mode="json"), task_input=item.model_dump(mode="json"))

        evaluation = await evaluator.evaluate(run, example)
        assert evaluation.score == 1.0
        assert evaluation.evaluator.id == evaluator.definition.id

        assert evaluation.comment == ""
        assert evaluation.model_dump()["error_details"] == []
        assert len(evaluation.model_dump()["error_details"]) == 0
