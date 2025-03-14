import uuid
from typing import Any, Optional, cast

import pytest

from core.domain.field_based_evaluation_config import FieldBasedEvaluationConfig, StringComparisonOptions
from core.domain.run_identifier import RunIdentifier
from core.domain.task_evaluator import EvalV2Evaluator, FieldBasedEvaluator, TaskEvaluator
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.models.task_evaluator import TaskEvaluatorDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_storage_test import TASK_ID, TENANT
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.evaluators import MongoEvaluatorStorage
from core.storage.mongo.utils import dump_model


@pytest.fixture(scope="function")
def evaluator_storage(storage: MongoStorage) -> MongoEvaluatorStorage:
    return cast(MongoEvaluatorStorage, storage.evaluators)


class TestAddTaskEvaluator:
    async def test_create(self, evaluator_storage: MongoEvaluatorStorage, task_evaluators_col: AsyncCollection) -> None:
        new_evaluator = TaskEvaluator(
            id="",
            name="hello",
            evaluator_type=FieldBasedEvaluator(config=FieldBasedEvaluationConfig(options=StringComparisonOptions())),
        )
        created = await evaluator_storage.add_task_evaluator(TASK_ID, 1, new_evaluator)
        new_evaluator.id = created.id
        assert created == new_evaluator
        assert created.id != ""

        updated = await task_evaluators_col.find_one({"task_id": TASK_ID, "task_schema_id": 1})
        assert updated
        assert str(updated["_id"]) == str(created.id)

    async def test_add_retrieve(self, evaluator_storage: MongoEvaluatorStorage) -> None:
        new_evaluator = TaskEvaluator(
            id="",
            name="hello",
            evaluator_type=FieldBasedEvaluator(config=FieldBasedEvaluationConfig(options=StringComparisonOptions())),
        )
        created = await evaluator_storage.add_task_evaluator(TASK_ID, 1, new_evaluator)

        retrieved = await evaluator_storage.get_task_evaluator(TASK_ID, 1, created.id)
        assert retrieved == created

        assert new_evaluator.id == "", "sanity"
        created2 = await evaluator_storage.add_task_evaluator(TASK_ID, 1, new_evaluator)
        assert created2.id != created.id

        all = [a async for a in evaluator_storage.list_task_evaluators(TASK_ID, 1)]
        assert len(all) == 2


def _task_evaluator(
    task_id: str = TASK_ID,
    schema_id: int = 1,
    name: Optional[str] = None,
    evaluator_type: str = "code_compare_outputs",
    **kwargs: Any,
) -> TaskEvaluatorDocument:
    doc = TaskEvaluatorDocument(
        _id=PyObjectID.new(),
        task_id=task_id,
        task_schema_id=schema_id,
        tenant=TENANT,
        name=name or str(uuid.uuid4()),
        metric="correctness",
        triggers=["auto", "manual"],
        uses_examples=False,
        evaluator_type=evaluator_type,
        properties=TaskEvaluatorDocument.Properties(
            python_code="print('hello world')",
        ),
        active=True,
    )
    return TaskEvaluatorDocument.model_validate({**doc.model_dump(by_alias=True), **kwargs})


class TestListTaskEvaluator:
    async def test_success(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
            _task_evaluator(tenant="t2"),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        evaluators = [a async for a in evaluator_storage.list_task_evaluators(TASK_ID, 1)]
        assert len(evaluators) == 2

    async def test_filter_single_type(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(
                evaluator_type="compare_outputs",
                properties=TaskEvaluatorDocument.Properties(
                    evaluator_task_id="1",
                    evaluator_task_schema_id=1,
                    evaluator_task_group=TaskEvaluatorDocument.Properties.Group(
                        id="1",
                        iteration=1,
                        tags=[],
                        properties={},
                    ),
                ),
            ),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
            _task_evaluator(tenant="t2"),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        evaluators = [a async for a in evaluator_storage.list_task_evaluators(TASK_ID, 1, types={"compare_outputs"})]
        assert len(evaluators) == 1
        assert evaluators[0].id == str(docs[0].id)

    async def test_filter_multiple_type(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(
                evaluator_type="compare_outputs",
                properties=TaskEvaluatorDocument.Properties(
                    evaluator_task_id="1",
                    evaluator_task_schema_id=1,
                    evaluator_task_group=TaskEvaluatorDocument.Properties.Group(
                        id="1",
                        iteration=1,
                        tags=[],
                        properties={},
                    ),
                ),
            ),
            _task_evaluator(),
            _task_evaluator(
                evaluator_type="evaluate_output",
                properties=TaskEvaluatorDocument.Properties(
                    evaluator_task_id="1",
                    evaluator_task_schema_id=1,
                    evaluator_task_group=TaskEvaluatorDocument.Properties.Group(
                        id="1",
                        iteration=1,
                        tags=[],
                        properties={},
                    ),
                ),
            ),
            _task_evaluator(schema_id=2),
            _task_evaluator(tenant="t2"),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        evaluators = [
            a
            async for a in evaluator_storage.list_task_evaluators(
                TASK_ID,
                1,
                types={"compare_outputs", "evaluate_output"},
            )
        ]
        assert len(evaluators) == 2
        assert {a.id for a in evaluators} == {str(docs[0].id), str(docs[2].id)}


class TestGetTaskEvaluator:
    async def test_success(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(name="user"),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        evaluator = await evaluator_storage.get_task_evaluator(TASK_ID, 1, str(docs[0].id))
        assert evaluator.id == str(docs[0].id)
        assert evaluator.name == "user"

    async def test_not_found(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(name="user"),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        with pytest.raises(ObjectNotFoundException):
            await evaluator_storage.get_task_evaluator(TASK_ID, 1, PyObjectID.new())


class TestDeleteTaskEvaluator:
    async def test_success(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(name="user"),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        await evaluator_storage.set_task_evaluator_active(TASK_ID, 1, str(docs[0].id), False)

        docs = [d async for d in task_evaluators_col.find({"task_id": TASK_ID, "task_schema_id": 1})]
        assert len(docs) == 2
        for doc in docs:
            assert doc["active"] == (doc["_id"] != docs[0]["_id"])

        evals = [a async for a in evaluator_storage.list_task_evaluators(TASK_ID, 1)]
        assert len(evals) == 1
        assert evals[0].id == str(docs[1]["_id"])

    async def test_not_found(
        self,
        evaluator_storage: MongoEvaluatorStorage,
        task_evaluators_col: AsyncCollection,
    ) -> None:
        docs = [
            _task_evaluator(name="user"),
            _task_evaluator(),
            _task_evaluator(schema_id=2),
        ]
        await task_evaluators_col.insert_many([dump_model(a) for a in docs])

        with pytest.raises(ObjectNotFoundException):
            await evaluator_storage.set_task_evaluator_active(TASK_ID, 1, PyObjectID.new(), False)


class TestPatchEvaluator:
    async def test_flow(self, evaluator_storage: MongoEvaluatorStorage) -> None:
        evaluator = await evaluator_storage.add_task_evaluator(
            TASK_ID,
            1,
            TaskEvaluator(
                id="",
                name="hello",
                active=False,
                is_loading=True,
                evaluator_type=EvalV2Evaluator(instructions=""),
            ),
        )
        assert evaluator.id != ""

        await evaluator_storage.patch_evaluator(
            evaluator.id,
            active=True,
            is_loading=False,
            evaluator_type=EvalV2Evaluator(
                instructions="blabl",
                instructions_updated_by=RunIdentifier(tenant="a", run_id="1", task_id="1", task_schema_id=1),
            ),
        )

        evaluator = await evaluator_storage.get_task_evaluator(TASK_ID, 1, evaluator.id)
        assert evaluator.active
        assert not evaluator.is_loading
        assert evaluator.evaluator_type == EvalV2Evaluator(
            instructions="blabl",
            instructions_updated_by=RunIdentifier(tenant="a", run_id="1", task_id="1", task_schema_id=1),
        )


class TestDeactivateEvaluators:
    async def test_success(self, evaluator_storage: MongoEvaluatorStorage) -> None:
        evaluator1 = await evaluator_storage.add_task_evaluator(
            TASK_ID,
            1,
            TaskEvaluator(
                id="",
                name="hello",
                evaluator_type=EvalV2Evaluator(instructions=""),
            ),
        )
        evaluator2 = await evaluator_storage.add_task_evaluator(
            TASK_ID,
            1,
            TaskEvaluator(
                id="",
                name="hello1",
                evaluator_type=EvalV2Evaluator(instructions=""),
            ),
        )

        await evaluator_storage.deactivate_evaluators(TASK_ID, 1, evaluator2.id, {"evalv2"})

        evaluators = [a async for a in evaluator_storage.list_task_evaluators(TASK_ID, 1, active=None)]
        assert len(evaluators) == 2, "sanity"
        evaluators.sort(key=lambda a: a.name)

        assert evaluators[0].id == evaluator1.id, "sanity"
        assert not evaluators[0].active
        assert evaluators[1].active
