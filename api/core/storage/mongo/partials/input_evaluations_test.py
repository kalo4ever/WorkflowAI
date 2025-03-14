import pytest

from core.domain.input_evaluation import InputEvaluation
from core.domain.run_identifier import RunIdentifier as DomainRunIdentifier
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.input_evaluation_document import InputEvaluationDocument
from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.models.run_identifier import RunOrUserIdentifier
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.input_evaluations import MongoInputEvaluationStorage
from core.storage.mongo.utils import dump_model


def _input_evaluation_doc(
    id: str = "666666666666666666666666",
    task_input_hash: str = "task_input_hash",
) -> InputEvaluationDocument:
    return InputEvaluationDocument(
        tenant="test_tenant",
        _id=PyObjectID.from_str(id),
        task_id="task_id",
        task_schema_id=1,
        task_input_hash=task_input_hash,
        correct_outputs=[{"a": 1}],
        incorrect_outputs=[{"a": 2}],
        evaluation_instruction="evaluation_instruction",
        generated_by=RunOrUserIdentifier(run_id="run_id", tenant="tenant", task_id="task_id", task_schema_id=1),
    )


@pytest.fixture()
def input_evaluation_storage(storage: MongoStorage):
    return storage.input_evaluations


class TestLatestInputEvaluation:
    async def test_single(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
        input_evaluations_col: AsyncCollection,
    ):
        input_evaluation_doc = _input_evaluation_doc()
        await input_evaluations_col.insert_one(dump_model(input_evaluation_doc))

        latest = await input_evaluation_storage.get_latest_input_evaluation(
            "task_id",
            1,
            "task_input_hash",
        )
        assert latest
        assert latest.id == "666666666666666666666666"

    async def test_fetch_latest(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
        input_evaluations_col: AsyncCollection,
    ):
        await input_evaluations_col.insert_many(
            [
                dump_model(d)
                for d in [
                    _input_evaluation_doc(),
                    _input_evaluation_doc(id="766666666666666666666666"),
                    _input_evaluation_doc(id="566666666666666666666666"),
                ]
            ],
        )

        latest = await input_evaluation_storage.get_latest_input_evaluation(
            "task_id",
            1,
            "task_input_hash",
        )
        assert latest
        assert latest.id == "766666666666666666666666"


class TestCreateInputEvaluation:
    async def test_single(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
    ):
        input_evaluation = InputEvaluation(
            task_input_hash="task_input_hash",
            correct_outputs=[{"a": 1}],
            incorrect_outputs=[{"a": 2}],
            evaluation_instruction="evaluation_instruction",
            created_by=DomainRunIdentifier(run_id="run_id", tenant="tenant", task_id="task_id", task_schema_id=1),
        )
        created = await input_evaluation_storage.create_input_evaluation(
            "task_id",
            1,
            input_evaluation,
        )

        assert created.id

        fetched = await input_evaluation_storage.get_input_evaluation(
            "task_id",
            1,
            created.id,
        )
        assert fetched
        assert fetched == created


class TestGetInputEvaluation:
    async def test_single(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
        input_evaluations_col: AsyncCollection,
    ):
        input_evaluation_doc = _input_evaluation_doc()
        await input_evaluations_col.insert_one(dump_model(input_evaluation_doc))

        fetched = await input_evaluation_storage.get_input_evaluation(
            "task_id",
            1,
            "666666666666666666666666",
        )
        assert fetched

        with pytest.raises(ObjectNotFoundException):
            await input_evaluation_storage.get_input_evaluation(
                "task_id",
                2,
                "666666666666666666666666",
            )


class TestListInputEvaluationsUniqueByHash:
    async def test_all_include(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
        input_evaluations_col: AsyncCollection,
    ):
        evaluations = [
            _input_evaluation_doc(),
            _input_evaluation_doc(id="766666666666666666666666", task_input_hash="task_input_hash_2"),
            _input_evaluation_doc(id="866666666666666666666666", task_input_hash="task_input_hash"),
        ]
        await input_evaluations_col.insert_many([dump_model(e) for e in evaluations])

        values = [e.id async for e in input_evaluation_storage.list_input_evaluations_unique_by_hash("task_id", 1)]
        values.sort()
        assert values == ["766666666666666666666666", "866666666666666666666666"]


class TestUniqueInputHashes:
    async def test_single(
        self,
        input_evaluation_storage: MongoInputEvaluationStorage,
        input_evaluations_col: AsyncCollection,
    ):
        evaluations = [
            _input_evaluation_doc(),
            _input_evaluation_doc(id="766666666666666666666666", task_input_hash="task_input_hash_2"),
            _input_evaluation_doc(id="866666666666666666666666", task_input_hash="task_input_hash"),
        ]
        await input_evaluations_col.insert_many([dump_model(e) for e in evaluations])

        hashes = await input_evaluation_storage.unique_input_hashes("task_id", 1)
        assert hashes == {"task_input_hash", "task_input_hash_2"}
