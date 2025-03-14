from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from core.domain.errors import DuplicateValueError
from core.domain.task_input import TaskInput, TaskInputQuery
from core.domain.task_variant import SerializableTaskVariant
from core.storage import ObjectNotFoundException
from core.storage.mongo.conftest import TENANT
from core.storage.mongo.models.task_input import TaskInputDocument
from core.storage.mongo.models.task_metadata import TaskMetadataSchema
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_storage_test import TASK_ID, _task_input  # pyright: ignore[reportPrivateUsage]
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.task_inputs import MongoTaskInputStorage
from core.storage.mongo.utils import dump_model
from core.storage.task_input_storage import TaskInputsStorage
from tests.models import task_variant


@pytest.fixture(scope="function")
def task_inputs_storage(storage: MongoStorage) -> MongoTaskInputStorage:
    return cast(MongoTaskInputStorage, storage.task_inputs)


def _task_input_doc(
    task_id: str = TASK_ID,
    schema_id: int = 1,
    input_hash: str = "1",
    **kwargs: Any,
) -> TaskInputDocument:
    return TaskInputDocument.model_validate(
        {
            "tenant": TENANT,
            "task": {"id": task_id, "schema_id": schema_id},
            "task_input_hash": input_hash,
            "task_input_preview": "a",
            "task_input": {"a": 1},
            **kwargs,
        },
    )


class TestCreateInputs:
    async def test_create_inputs(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        inputs = [
            TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a"),
            TaskInput(task_input_hash="2", task_input={"a": 2}, task_input_preview="b"),
        ]
        task = task_variant()

        await task_inputs_storage.create_inputs(task, inputs)

        stored_inputs = [i async for i in task_inputs_col.find({})]
        assert len(stored_inputs) == 2
        stored_inputs.sort(key=lambda x: x["task_input_hash"])

        assert stored_inputs[0]["task_input"] == {"a": 1}
        assert stored_inputs[1]["task_input"] == {"a": 2}

    async def test_create_inputs_duplicates(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        inputs = [
            TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a"),
        ]

        task = task_variant()
        await task_inputs_storage.create_inputs(task, inputs)

        assert await task_inputs_col.count_documents({}) == 1, "Sanity"

        inputs = [
            TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a"),
            TaskInput(task_input_hash="2", task_input={"a": 2}, task_input_preview="b"),
        ]
        await task_inputs_storage.create_inputs(task, inputs)

        assert await task_inputs_col.count_documents({}) == 2

        stored_inputs = [i async for i in task_inputs_col.find({})]
        assert len(stored_inputs) == 2
        stored_inputs.sort(key=lambda x: x["task_input_hash"])

        assert stored_inputs[0]["task_input"] == {"a": 1}
        assert stored_inputs[1]["task_input"] == {"a": 2}

    async def test_create_inputs_duplicates_datasets(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        inputs = [
            TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a"),
            TaskInput(task_input_hash="2", task_input={"a": 2}, task_input_preview="a", datasets={"ds3"}),
        ]

        task = task_variant()
        await task_inputs_storage.create_inputs(task, inputs)

        assert await task_inputs_col.count_documents({}) == 2, "Sanity"

        inputs = [
            TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a", datasets={"ds1"}),
            TaskInput(task_input_hash="2", task_input={"a": 2}, task_input_preview="a", datasets={"ds1", "ds2"}),
            TaskInput(task_input_hash="3", task_input={"a": 3}, task_input_preview="a", datasets={"ds1"}),
        ]
        await task_inputs_storage.create_inputs(task, inputs)

        assert await task_inputs_col.count_documents({}) == 3

        stored_inputs = [i async for i in task_inputs_col.find({})]
        assert len(stored_inputs) == 3
        stored_inputs.sort(key=lambda x: x["task_input_hash"])

        assert sorted(stored_inputs[0]["datasets"]) == ["ds1"]
        assert sorted(stored_inputs[1]["datasets"]) == ["ds1", "ds2", "ds3"]
        assert sorted(stored_inputs[2]["datasets"]) == ["ds1"]


class TestCreateInput:
    async def test_create_single(self, task_inputs_storage: MongoTaskInputStorage, task_inputs_col: AsyncCollection):
        input = TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a")
        task = task_variant()

        await task_inputs_storage.create_input(task, input)

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "1"})
        assert doc is not None

    async def test_create_duplicate(self, task_inputs_storage: MongoTaskInputStorage, task_inputs_col: AsyncCollection):
        input = TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a")
        task = task_variant()
        await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 1, "Sanity"

        with pytest.raises(DuplicateValueError):
            await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 1

    async def test_create_dupl_different_schema(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        input = TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a")
        task = task_variant()
        await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 1, "Sanity"

        task.task_schema_id = 2
        await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 2

    async def test_create_dupl_different_task_id(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        input = TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a")
        task = task_variant()
        await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 1, "Sanity"

        task.task_id = "bla"
        await task_inputs_storage.create_input(task, input)

        assert await task_inputs_col.count_documents({}) == 2

    async def test_create_with_datasets(
        self,
        task_inputs_storage: MongoTaskInputStorage,
        task_inputs_col: AsyncCollection,
    ):
        input = TaskInput(task_input_hash="1", task_input={"a": 1}, task_input_preview="a")
        task = task_variant()

        await task_inputs_storage.create_input(task, input)

        input2 = input.model_copy()
        input2.datasets = {"ds1", "ds2"}
        with pytest.raises(DuplicateValueError):
            await task_inputs_storage.create_input(task, input2)


class TestAttachExample:
    async def test_attach_example(self, task_inputs_storage: MongoTaskInputStorage, task_inputs_col: AsyncCollection):
        await task_inputs_col.insert_many(
            [
                dump_model(d)
                for d in [
                    _task_input_doc(),
                    _task_input_doc(input_hash="2"),
                ]
            ],
        )

        await task_inputs_storage.attach_example(TASK_ID, 1, "1", "ex1", "ex2")

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "1"})
        assert doc is not None
        assert doc["example_id"] == "ex1"
        assert doc["example_preview"] == "ex2"

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "2"})
        assert doc is not None
        assert "example_id" not in doc


class TestDetachExample:
    async def test_detach_example(self, task_inputs_storage: MongoTaskInputStorage, task_inputs_col: AsyncCollection):
        await task_inputs_col.insert_many(
            [
                dump_model(d)
                for d in [
                    _task_input_doc(),
                    _task_input_doc(input_hash="2", example_id="ex1", example_preview="ex2"),
                ]
            ],
        )

        await task_inputs_storage.detach_example(TASK_ID, 1, "2", "ex1")

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "2"})
        assert doc is not None
        assert "example_id" not in doc
        assert "example_preview" not in doc

        # Making sure calling it again raises
        with pytest.raises(ObjectNotFoundException):
            await task_inputs_storage.detach_example(TASK_ID, 1, "2", "ex1")


class TestRemoveInputsFromDataset:
    async def test_success(self, task_inputs_storage: MongoTaskInputStorage, task_inputs_col: AsyncCollection):
        await task_inputs_col.insert_many(
            [
                dump_model(d)
                for d in [
                    _task_input_doc(input_hash="1", datasets={"ds1", "ds2"}),
                    _task_input_doc(input_hash="2", datasets={"ds1", "ds2"}),
                    _task_input_doc(input_hash="3", datasets={"ds1", "ds2"}),
                ]
            ],
        )

        await task_inputs_storage.remove_inputs_from_datasets(TASK_ID, 1, "ds1", ["1", "3"])

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "1"})
        assert doc is not None
        assert doc["datasets"] == ["ds2"]

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "2"})
        assert doc is not None
        assert sorted(doc["datasets"]) == ["ds1", "ds2"]

        doc = await task_inputs_col.find_one({"task.id": TASK_ID, "task.schema_id": 1, "task_input_hash": "3"})
        assert doc is not None
        assert doc["datasets"] == ["ds2"]


class TestListInputs:
    @pytest.fixture(scope="function")
    def task_fixt(self):
        return task_variant()

    @pytest.fixture(scope="function")
    async def task_inputs_fixt(
        self,
        task_fixt: SerializableTaskVariant,
        task_inputs_col: AsyncCollection,
        storage: MongoStorage,
    ):
        metadata = TaskMetadataSchema.from_resource(task_fixt)
        inputs = [
            TaskInputDocument(
                tenant=TENANT,
                task=metadata,
                task_input_hash="1",
                task_input={"a": 1},
                task_input_preview="a",
            ),
            TaskInputDocument(
                tenant=TENANT,
                task=metadata,
                task_input_hash="2",
                task_input={"a": 2},
                task_input_preview="b",
            ),
            TaskInputDocument(
                tenant="t1",
                task=metadata,
                task_input_hash="3",
                task_input={"a": 3},
                task_input_preview="c",
            ),
            TaskInputDocument(
                tenant=TENANT,
                task=TaskMetadataSchema(id=task_fixt.id, schema_id=task_fixt.task_schema_id + 1),
                task_input_hash="4",
                task_input={"b": 3},
                task_input_preview="d",
            ),
        ]
        await task_inputs_col.insert_many([dump_model(a) for a in inputs])
        return inputs

    async def test_list_inputs(self, task_inputs_storage: TaskInputsStorage, task_inputs_fixt: list[TaskInputDocument]):
        query = TaskInputQuery(task_id=TASK_ID, task_schema_id=1)

        inputs = [i async for i in task_inputs_storage.list_inputs(query)]
        assert len(inputs) == 2

        inputs.sort(key=lambda x: x.task_input_hash)
        assert inputs[0].task_input == {"a": 1}
        assert inputs[1].task_input == {"a": 2}

    async def test_list_inputs_exclude_fields(
        self,
        task_inputs_storage: TaskInputsStorage,
        task_inputs_fixt: list[TaskInputDocument],
    ):
        query = TaskInputQuery(task_id=TASK_ID, task_schema_id=1, exclude_fields={"task_input"})

        inputs = [i async for i in task_inputs_storage.list_inputs(query)]
        assert len(inputs) == 2

        for i in inputs:
            assert i.task_input is None

    async def test_unicity(self, task_inputs_col: AsyncCollection, storage: MongoStorage):
        input = TaskInputDocument(
            tenant=TENANT,
            task=TaskMetadataSchema(id="1", schema_id=1),
            task_input_hash="1",
            task_input={"a": 1},
            task_input_preview="a",
        )
        await task_inputs_col.insert_one(dump_model(input))

        # Inserting an input with the same hash should throw
        with pytest.raises(DuplicateKeyError):
            await task_inputs_col.insert_one(dump_model(input))

        assert input.task is not None
        # Inserting an input with the same hash but different task id should work
        input.task.id = "2"
        await task_inputs_col.insert_one(dump_model(input))

        # Inserting an input with the same hash but different schema id should work
        input.task.id = "1"
        input.task.schema_id = 2
        await task_inputs_col.insert_one(dump_model(input))

        count = await task_inputs_col.count_documents({})
        assert count == 3, "sanity"

    async def test_inputs_in_datasets(self, task_inputs_col: AsyncCollection, task_inputs_storage: TaskInputsStorage):
        inputs = [
            _task_input(datasets=["1"], task_input_hash="1"),
            _task_input(datasets=["2"], task_input_hash="2"),
            _task_input(datasets=["1", "2"], task_input_hash="3"),
            _task_input(datasets=None, task_input_hash="4"),
        ]
        await task_inputs_col.insert_many([dump_model(a) for a in inputs])

        query = TaskInputQuery(task_id=TASK_ID, task_schema_id=1, dataset_id="1")
        inputs = [i async for i in task_inputs_storage.list_inputs(query)]
        assert len(inputs) == 2

        hashes = {i.task_input_hash for i in inputs}
        assert hashes == {"1", "3"}
