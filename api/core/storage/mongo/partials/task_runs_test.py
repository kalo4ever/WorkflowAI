import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory

from core.domain.task_run_aggregate_per_day import TaskRunAggregatePerDay
from core.domain.task_run_query import SerializableTaskRunField, SerializableTaskRunQuery
from core.storage import TaskTuple
from core.storage.mongo.models.task_metadata import TaskMetadataSchema
from core.storage.mongo.models.task_run_document import TaskRunDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.task_runs import MongoTaskRunStorage
from core.storage.mongo.utils import dump_model
from core.utils.dicts import get_at_keypath_str

from ..mongo_storage_test import TASK_ID, _task_run  # pyright: ignore [reportPrivateUsage]


@pytest.fixture
def task_run_storage(storage: MongoStorage):
    return MongoTaskRunStorage(storage._tenant_tuple, storage._task_runs_collection)  # pyright: ignore [reportPrivateUsage]


class TestAggregateTaskRunCosts:
    async def test_aggregate_task_run_costs(self, task_run_storage: MongoTaskRunStorage, task_run_col: AsyncCollection):
        runs = [
            _task_run(
                _id="run1",
                cost_usd=10.0,
                is_free=False,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run2",
                cost_usd=20.0,
                is_free=False,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run3",
                cost_usd=0.0,
                is_free=False,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run4",
                cost_usd=15.0,
                is_free=False,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run5",
                cost_usd=5.0,
                is_free=False,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run6",
                cost_usd=25.0,
                is_free=False,
                created_at=datetime(2023, 1, 5, tzinfo=timezone.utc),
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = task_run_storage.aggregate_task_run_costs(
            1,
            SerializableTaskRunQuery(
                task_id=TASK_ID,
                task_schema_id=None,
                created_after=datetime(2023, 1, 1, tzinfo=timezone.utc),
                created_before=datetime(2023, 1, 6, tzinfo=timezone.utc),
            ),
        )

        async for aggregated_cost in aggregated_costs:
            if aggregated_cost.date == date(2023, 1, 1):
                assert aggregated_cost.total_count == 3
                assert aggregated_cost.total_cost_usd == 35.0
            elif aggregated_cost.date == date(2023, 1, 2):
                assert aggregated_cost.total_count == 2
                assert aggregated_cost.total_cost_usd == 15.0
            elif aggregated_cost.date == date(2023, 1, 5):
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 25.0
            else:
                assert False, "Unexpected date"

    async def test_aggregate_task_run_costs_some_free(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        # Check that free runs are counted
        # Check that free runs cost is not counted.
        runs = [
            _task_run(
                _id="run1",
                cost_usd=10.0,
                is_free=False,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run2",
                cost_usd=20.0,
                is_free=True,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run3",
                cost_usd=0.0,
                is_free=False,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run4",
                cost_usd=15.0,
                is_free=True,
                created_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run5",
                cost_usd=5.0,
                is_free=False,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            ),
            _task_run(
                _id="run6",
                cost_usd=25.0,
                is_free=False,
                created_at=datetime(2023, 1, 5, tzinfo=timezone.utc),
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = task_run_storage.aggregate_task_run_costs(
            1,
            SerializableTaskRunQuery(
                task_id=TASK_ID,
                task_schema_id=None,
                created_after=datetime(2023, 1, 1, tzinfo=timezone.utc),
                created_before=datetime(2023, 1, 6, tzinfo=timezone.utc),
            ),
        )

        async for aggregated_cost in aggregated_costs:
            if aggregated_cost.date == date(2023, 1, 1):
                assert aggregated_cost.total_count == 3
                assert aggregated_cost.total_cost_usd == 15.0
            elif aggregated_cost.date == date(2023, 1, 2):
                assert aggregated_cost.total_count == 2
                assert aggregated_cost.total_cost_usd == 0.0
            elif aggregated_cost.date == date(2023, 1, 5):
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 25.0
            else:
                assert False, "Unexpected date"

    async def test_aggregate_task_run_costs_some_free_last_week(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        current_date = datetime.now()
        runs = [
            _task_run(
                _id="run1",
                cost_usd=10.0,
                is_free=False,
                created_at=current_date,
            ),
            _task_run(
                _id="run2",
                cost_usd=20.0,
                is_free=False,
                created_at=current_date - timedelta(days=1),
            ),
            _task_run(
                _id="run3",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=3),
            ),
            _task_run(
                _id="run4",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=3),
            ),
            _task_run(
                _id="run5",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=4),
            ),
            _task_run(
                _id="run6",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=3),
            ),
            _task_run(
                _id="run7",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=9),
            ),
            _task_run(
                _id="run8",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=8),
            ),
            _task_run(
                _id="run9",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=8),
            ),
            _task_run(
                _id="run10",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=7),
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = [
            a
            async for a in task_run_storage.aggregate_task_run_costs(
                1,
                SerializableTaskRunQuery(
                    task_id=TASK_ID,
                    task_schema_id=None,
                    created_after=current_date - timedelta(6),
                    created_before=current_date,
                ),
            )
        ]
        sorted_aggregated_costs = sorted(list(aggregated_costs), key=lambda x: x.date)
        assert len(sorted_aggregated_costs) == 4

        assert sorted_aggregated_costs == [
            TaskRunAggregatePerDay(date=(current_date - timedelta(4)).date(), total_count=1, total_cost_usd=5.0),
            TaskRunAggregatePerDay(date=(current_date - timedelta(3)).date(), total_count=3, total_cost_usd=40.0),
            TaskRunAggregatePerDay(date=(current_date - timedelta(1)).date(), total_count=1, total_cost_usd=20.0),
            TaskRunAggregatePerDay(date=current_date.date(), total_count=1, total_cost_usd=10.0),
        ]

    async def test_aggregate_task_run_costs_some_free_last_month(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        current_date = datetime.now()
        runs = [
            _task_run(
                _id="run1",
                cost_usd=10.0,
                is_free=False,
                created_at=current_date - timedelta(days=30),
            ),
            _task_run(
                _id="run2",
                cost_usd=20.0,
                is_free=False,
                created_at=current_date - timedelta(days=29),
            ),
            _task_run(
                _id="run3",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=27),
            ),
            _task_run(
                _id="run4",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=27),
            ),
            _task_run(
                _id="run5",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=28),
            ),
            _task_run(
                _id="run6",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=27),
            ),
            _task_run(
                _id="run7",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=33),
            ),
            _task_run(
                _id="run8",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=32),
            ),
            _task_run(
                _id="run9",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=32),
            ),
            _task_run(
                _id="run10",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=31),
            ),
            _task_run(
                _id="run11",
                cost_usd=3.0,
                is_free=False,
                created_at=current_date,
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = task_run_storage.aggregate_task_run_costs(
            1,
            SerializableTaskRunQuery(
                task_id=TASK_ID,
                task_schema_id=None,
                created_after=current_date - timedelta(29),
                created_before=current_date,
            ),
        )

        async for aggregated_cost in aggregated_costs:
            if aggregated_cost.date == (current_date - timedelta(29)).date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 20.0
            elif aggregated_cost.date == (current_date - timedelta(28)).date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 5.0
            elif aggregated_cost.date == (current_date - timedelta(27)).date():
                assert aggregated_cost.total_count == 3
                assert aggregated_cost.total_cost_usd == 40.0
            elif aggregated_cost.date == current_date.date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 3.0
            else:
                assert False, "Unexpected date"

    async def test_aggregate_task_run_costs_some_free_last_year(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        current_date = datetime.now()
        runs = [
            _task_run(
                _id="run1",
                cost_usd=10.0,
                is_free=False,
                created_at=current_date - timedelta(days=365),
            ),
            _task_run(
                _id="run2",
                cost_usd=20.0,
                is_free=False,
                created_at=current_date - timedelta(days=290),
            ),
            _task_run(
                _id="run3",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=270),
            ),
            _task_run(
                _id="run4",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=270),
            ),
            _task_run(
                _id="run5",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=280),
            ),
            _task_run(
                _id="run6",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=270),
            ),
            _task_run(
                _id="run7",
                cost_usd=0.0,
                is_free=False,
                created_at=current_date - timedelta(days=376),
            ),
            _task_run(
                _id="run8",
                cost_usd=15.0,
                is_free=False,
                created_at=current_date - timedelta(days=376),
            ),
            _task_run(
                _id="run9",
                cost_usd=5.0,
                is_free=False,
                created_at=current_date - timedelta(days=382),
            ),
            _task_run(
                _id="run10",
                cost_usd=25.0,
                is_free=False,
                created_at=current_date - timedelta(days=391),
            ),
            _task_run(
                _id="run11",
                cost_usd=3.0,
                is_free=False,
                created_at=current_date,
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = task_run_storage.aggregate_task_run_costs(
            1,
            SerializableTaskRunQuery(
                task_id=TASK_ID,
                task_schema_id=None,
                created_after=current_date - timedelta(364),
                created_before=current_date,
            ),
        )

        async for aggregated_cost in aggregated_costs:
            if aggregated_cost.date == (current_date - timedelta(290)).date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 20.0
            elif aggregated_cost.date == (current_date - timedelta(280)).date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 5.0
            elif aggregated_cost.date == (current_date - timedelta(270)).date():
                assert aggregated_cost.total_count == 3
                assert aggregated_cost.total_cost_usd == 40.0
            elif aggregated_cost.date == current_date.date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 3.0
            else:
                assert False, "Unexpected date"

    async def test_aggregate_task_run_costs_some_free_last_month_one_task(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        current_date = datetime.now()
        runs = [
            _task_run(
                _id="run1",
                task_id="task1",
                cost_usd=10.0,
                is_free=False,
                created_at=current_date - timedelta(days=29),
            ),
            _task_run(
                _id="run2",
                task_id="task2",
                cost_usd=20.0,
                is_free=False,
                created_at=current_date - timedelta(days=29),
            ),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        aggregated_costs = task_run_storage.aggregate_task_run_costs(
            1,
            SerializableTaskRunQuery(
                task_id="task2",
                task_schema_id=None,
                created_after=current_date - timedelta(29),
                created_before=current_date,
            ),
        )

        async for aggregated_cost in aggregated_costs:
            if aggregated_cost.date == (current_date - timedelta(29)).date():
                assert aggregated_cost.total_count == 1
                assert aggregated_cost.total_cost_usd == 20.0
            else:
                assert False, "Unexpected date"


class TestAggregateTokenCounts:
    async def test_aggregate_token_counts(self, task_run_col: AsyncCollection, task_run_storage: MongoTaskRunStorage):
        task_runs = [
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 12, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 15, "completion_token_count": 25}},
                ],
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 9, "completion_token_count": 15}},
                ],
            ),
        ]
        await task_run_col.insert_many([dump_model(t) for t in task_runs])

        result = await task_run_storage.aggregate_token_counts(_TASK_TUPLE, 1)

        expected_prompt_avg = (12 + 15 + 9) / 3
        expected_completion_avg = (20 + 25 + 15) / 3
        assert result["average_prompt_tokens"] == expected_prompt_avg
        assert result["average_completion_tokens"] == expected_completion_avg

    async def test_aggregate_token_counts_o1(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
    ):
        task_runs = [
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 12, "completion_token_count": 20}},
                ],
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 13, "completion_token_count": 200}},
                ],
                model="o1-preview-2024-09-12",
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 14, "completion_token_count": 201}},
                ],
                model="o1-mini-2024-09-12",
            ),
        ]
        await task_run_col.insert_many([dump_model(t) for t in task_runs])

        result = await task_run_storage.aggregate_token_counts(
            _TASK_TUPLE,
            1,
            excluded_models=["o1-preview-2024-09-12", "o1-mini-2024-09-12"],
        )

        assert result["average_prompt_tokens"] == 12
        assert result["average_completion_tokens"] == 20


class TestGetSuggestions:
    async def test_get_suggestions(self, task_run_col: AsyncCollection, task_run_storage: MongoTaskRunStorage):
        task_runs = [
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 12, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 15, "completion_token_count": 25}},
                ],
                task_input={"name": "test", "age": 10},
                task_output={"result": "test output", "group": "child", "responsibility_group": "youth"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=1,
                llm_completions=[
                    {"usage": {"prompt_token_count": 120, "completion_token_count": 200}},
                    {"usage": {"prompt_token_count": 150, "completion_token_count": 250}},
                ],
                task_input={"name": "test1", "age": 17},
                task_output={"result": "test1 output1", "group": "teenager", "responsibility_group": "youth"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=2,
                llm_completions=[
                    {"usage": {"prompt_token_count": 1200, "completion_token_count": 2000}},
                    {"usage": {"prompt_token_count": 1500, "completion_token_count": 2500}},
                ],
                task_input={"name": "test2", "age": 24},
                task_output={"result": "test2 output2", "group": "youth", "responsibility_group": "adult"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=2,
                llm_completions=[
                    {"usage": {"prompt_token_count": 120, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 1500, "completion_token_count": 25000}},
                ],
                task_input={"name": "test3", "age": 30},
                task_output={"result": "test3 output3", "group": "adult", "responsibility_group": "adult"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=3,
                llm_completions=[
                    {"usage": {"prompt_token_count": 1200, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 15, "completion_token_count": 25}},
                ],
                task_input={"name": "test4", "age": 35},
                task_output={"result": "test4 output4", "group": "adult", "responsibility_group": "adult"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=3,
                llm_completions=[
                    {"usage": {"prompt_token_count": 12, "completion_token_count": 250}},
                    {"usage": {"prompt_token_count": 15, "completion_token_count": 23}},
                ],
                task_input={"name": "test5", "age": 40},
                task_output={"result": "test5 output5", "group": "adult", "responsibility_group": "adult"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=3,
                llm_completions=[
                    {"usage": {"prompt_token_count": 1200, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 1500, "completion_token_count": 250}},
                ],
                task_input={"name": "test6", "age": 55},
                task_output={"result": "test6 output6", "group": "adult", "responsibility_group": "adult"},
            ),
            _task_run(
                task_id=TASK_ID,
                task_schema_id=3,
                llm_completions=[
                    {"usage": {"prompt_token_count": 18, "completion_token_count": 20}},
                    {"usage": {"prompt_token_count": 23, "completion_token_count": 23}},
                ],
                task_input={"name": "test3", "age": 75},
                task_output={"result": "test3 output7", "group": "senior", "responsibility_group": "senior"},
            ),
        ]
        await task_run_col.insert_many([dump_model(t) for t in task_runs])

        suggestions = task_run_storage.get_suggestions(
            TASK_ID,
            ["task_input.age"],
        )
        suggestions = await suggestions
        assert len(suggestions) == 1
        assert suggestions["task_input.age"] is not None
        assert sorted(suggestions["task_input.age"]) == [10, 17, 24, 30, 35, 40, 55, 75]

        suggestions = task_run_storage.get_suggestions(
            TASK_ID,
            ["task_output.responsibility_group", "task_output.group"],
        )
        suggestions = await suggestions
        assert len(suggestions) == 2
        assert suggestions["task_output.responsibility_group"] is not None
        assert sorted(suggestions["task_output.responsibility_group"]) == ["adult", "senior", "youth"]
        assert suggestions["task_output.group"] is not None
        assert sorted(suggestions["task_output.group"]) == ["adult", "child", "senior", "teenager", "youth"]

        suggestions = task_run_storage.get_suggestions(
            TASK_ID,
            [
                "task_input.name",
                "task_input.age",
                "task_output.responsibility_group",
                "task_output.group",
                "task_output.result",
                "llm_completions.usage.prompt_token_count",
                "llm_completions.usage.completion_token_count",
            ],
        )
        suggestions = await suggestions
        assert len(suggestions) == 7
        assert suggestions["task_input.name"] is not None
        assert sorted(suggestions["task_input.name"]) == [
            "test",
            "test1",
            "test2",
            "test3",
            "test4",
            "test5",
            "test6",
        ]
        assert suggestions["task_input.age"] is not None
        assert sorted(suggestions["task_input.age"]) == [10, 17, 24, 30, 35, 40, 55, 75]
        assert suggestions["task_output.responsibility_group"] is not None
        assert sorted(suggestions["task_output.responsibility_group"]) == ["adult", "senior", "youth"]
        assert suggestions["task_output.group"] is not None
        assert sorted(suggestions["task_output.group"]) == ["adult", "child", "senior", "teenager", "youth"]
        assert suggestions["task_output.result"] is not None
        assert sorted(suggestions["task_output.result"]) == [
            "test output",
            "test1 output1",
            "test2 output2",
            "test3 output3",
            "test3 output7",
            "test4 output4",
            "test5 output5",
            "test6 output6",
        ]
        assert suggestions["llm_completions.usage.prompt_token_count"] is not None
        assert sorted(suggestions["llm_completions.usage.prompt_token_count"]) == [
            12.0,
            15.0,
            18.0,
            23.0,
            120.0,
            150.0,
            1200.0,
            1500.0,
        ]
        assert suggestions["llm_completions.usage.completion_token_count"] is not None
        assert sorted(suggestions["llm_completions.usage.completion_token_count"]) == [
            20.0,
            23.0,
            25.0,
            200.0,
            250.0,
            2000.0,
            2500.0,
            25000.0,
        ]


class TestAggregateRuns:
    async def test_simple(self, task_run_col: AsyncCollection, task_run_storage: MongoTaskRunStorage):
        runs = [
            # Another tenant, should be ignored
            _task_run(tenant="another_tenant", cost_usd=110.75),
            # Another task schema, should be ignored
            _task_run(task_schema_id=3, cost_usd=102.0),
            _task_run(
                cost_usd=1.0,
                user_review="positive",
                task_input_hash="i1",
                task_output_hash="o1",
                duration_seconds=1,
            ),
            # Insert a run for a duplicate input & output, it should not be ignored
            _task_run(
                cost_usd=1.0,
                user_review="positive",
                task_input_hash="i1",
                task_output_hash="o1",
                duration_seconds=1,
            ),
            # Insert a run for a duplicate input, it should NOT be ignored
            _task_run(cost_usd=2.0, user_review="negative", task_input_hash="i1"),
            _task_run(cost_usd=3.0, ai_review="unsure"),
            _task_run(cost_usd=4.0, ai_review="negative"),
            # User review should prime
            _task_run(cost_usd=5.0, ai_review="positive", user_review="negative"),
            _task_run(cost_usd=6.0, error=TaskRunDocument.Error(), status="failure"),
            _task_run(cost_usd=7.0, ai_review="in_progress"),
            # no review
            _task_run(),
            _task_run(version_id="2", cost_usd=1, duration_seconds=2),
        ]
        await task_run_col.insert_many([dump_model(r) for r in runs])

        agg = await task_run_storage.aggregate_runs((TASK_ID, 1), 1, set(), None)
        assert len(agg) == 2

        assert agg["group_hash"].get("average_cost_usd") == 3.625
        assert agg["group_hash"].get("average_duration_seconds") == 1.0
        assert agg["group_hash"].get("total_run_count") == 9
        assert agg["group_hash"].get("failed_run_count") == 1
        assert len(agg["group_hash"].get("eval_hashes", [])) == 9

        assert agg["2"].get("average_cost_usd") == 1.0
        assert agg["2"].get("average_duration_seconds") == 2.0
        assert agg["2"].get("total_run_count") == 1
        assert agg["2"].get("failed_run_count") == 0
        assert len(agg["2"].get("eval_hashes", [])) == 1


class TestSearchRunsInclude:
    async def test_fields_exist(self, task_run_storage: MongoTaskRunStorage):
        includes = task_run_storage._search_run_include()  # pyright: ignore [reportPrivateUsage]
        includes.remove("user_review")
        includes.remove("ai_review")
        # We should get all fields with None values
        dumped = TaskRunDocument(task=TaskMetadataSchema()).model_dump(by_alias=True)

        with pytest.raises(KeyError):  # sanity
            get_at_keypath_str(dumped, "nonexistent")

        for field in includes:
            # Check that it does not raise
            get_at_keypath_str(dumped, field)


def _run_query(task_id: str = TASK_ID, task_schema_id: int = 1, **kwargs: Any) -> SerializableTaskRunQuery:
    return SerializableTaskRunQuery(
        task_id=task_id,
        task_schema_id=task_schema_id,
        **kwargs,
    )


_TASK_TUPLE: TaskTuple = (TASK_ID, 1)


class TestFetchRunResources:
    @pytest.fixture(scope="function")
    async def runs(self, task_run_col: AsyncCollection, storage: MongoStorage) -> list[TaskRunDocument]:
        runs = [
            _task_run(),
            # Making sure these 2 are ordered by id
            _task_run(task_input_hash="2"),
            _task_run(task_input_hash="2", created_at=datetime(1970, 1, 1)),
            _task_run(task_id="2"),
            _task_run(task_schema_id=2),
            _task_run(status="failure", user_review="positive"),
        ]
        res = await task_run_col.insert_many([dump_model(a) for a in runs])
        for i, ex in enumerate(runs):
            ex.id = res.inserted_ids[i]
        return runs

    @pytest.mark.parametrize(
        "query,expected",  # expected is a set of example idx in the examples list
        [
            (_run_query(status={"success"}), {0, 1, 2}),
            (_run_query(status={"success"}, exclude_fields={"task_input"}), {0, 1, 2}),
            (_run_query(status={"success"}, unique_by={"task_input_hash"}, sort_by="recent"), {0, 1}),
            (_run_query(status={"success"}, exclude_fields={"task_output"}), {0, 1, 2}),
            (_run_query(status={"failure"}), {5}),
            (_run_query(status=None), {0, 1, 2, 5}),
        ],
    )
    async def test_fetch_run_resources(
        self,
        runs: list[TaskRunDocument],
        task_run_storage: MongoTaskRunStorage,
        query: SerializableTaskRunQuery,
        expected: set[int],
    ) -> None:
        fetched = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(fetched) == len(expected)

        idx_set = set[int]()
        for ex in fetched:
            if query.exclude_fields:
                if "task_input" not in query.exclude_fields:
                    assert ex.task_input
                if "task_output" not in query.exclude_fields:
                    assert ex.task_output
            # get the index of the example in the examples list
            idx = next(i for i, e in enumerate(runs) if e.id == ex.id)
            idx_set.add(idx)

        assert idx_set == expected

    async def test_metadata(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
    ):
        task_runs = [
            _task_run(id="1", metadata={"key1": "value1", "key2": "value2"}),
            _task_run(id="2", metadata={"key1": "value1"}),
            _task_run(id="3", metadata={"key3": "value3"}),
        ]
        await task_run_col.insert_many([dump_model(a) for a in task_runs])

        query = SerializableTaskRunQuery(task_id=TASK_ID, task_schema_id=1, metadata={"key1": "value1"})
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(runs) == 2

    async def test_fetch_unique_input_hash(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
    ):
        task_runs = [
            _task_run(id="1", task_input_hash="1"),
            _task_run(id="2", task_input_hash="2"),
            _task_run(id="3", task_input_hash="2"),
        ]
        await task_run_col.insert_many([dump_model(a) for a in task_runs])

        """Test label filters for different combination of labels"""
        query = SerializableTaskRunQuery(task_id=TASK_ID, task_schema_id=1, status={"success"})
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(runs) == 3, "Sanity"

        query.unique_by = {"task_input_hash"}
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(runs) == 2

    async def test_unique_by_multiple(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
    ):
        task_runs = [
            _task_run(id="1", task_input_hash="1", task_output_hash="1"),
            _task_run(id="2", task_input_hash="2", task_output_hash="2"),
            _task_run(id="3", task_input_hash="2", task_output_hash="2"),
            _task_run(id="4", task_input_hash="2", task_output_hash="3"),
        ]
        await task_run_col.insert_many([dump_model(a) for a in task_runs])

        query = SerializableTaskRunQuery(
            task_id=TASK_ID,
            task_schema_id=1,
            unique_by={"task_input_hash", "task_output_hash"},
            status={"success"},
        )
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(runs) == 3

    @pytest.mark.parametrize("field", ("task_input_hash", "group.iteration"))
    async def test_include_field(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
        field: SerializableTaskRunField,
    ) -> None:
        task_runs = [
            _task_run(id="1", task_input_hash="1"),
            _task_run(id="2", task_input_hash="2"),
            _task_run(id="3", task_input_hash="2"),
        ]
        await task_run_col.insert_many([dump_model(a) for a in task_runs])

        query = SerializableTaskRunQuery(task_id=TASK_ID, task_schema_id=1, include_fields={field}, status={"success"})

        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert len(runs) == 3

        field_keys = field.split(".")
        for run in runs:
            dumped = run.model_dump()

            for key in field_keys:
                assert key in dumped
                dumped = dumped[key]

            assert dumped

    async def test_created_after(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
        frozen_time: FrozenDateTimeFactory,
    ):
        await task_run_col.insert_one(dump_model(_task_run(id="1", created_at=datetime.now())))

        query = SerializableTaskRunQuery(
            task_id=TASK_ID,
            task_schema_id=1,
            include_fields={"_id", "created_at"},
            status={"success"},
        )
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert [a.id for a in runs] == ["1"]

        frozen_time.tick()

        await task_run_col.insert_one(dump_model(_task_run(id="2", created_at=datetime.now())))

        runs_1 = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert [a.id for a in runs_1] == ["2", "1"]

        query.created_after = runs_1[1].created_at
        runs_2 = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        assert [a.id for a in runs_2] == ["2"]

    async def test_by_status_indexed(
        self,
        task_run_col: AsyncCollection,
        task_run_storage: MongoTaskRunStorage,
        system_profile_col: AsyncCollection,
    ):
        task_runs = [
            _task_run(id="1", status="success"),
            _task_run(id="2", status="failure"),
            _task_run(id="3", status="success"),
        ]
        await task_run_col.insert_many([dump_model(a) for a in task_runs])

        query = SerializableTaskRunQuery(task_id=TASK_ID, task_schema_id=1, status={"success"})
        runs = [a async for a in task_run_storage.fetch_task_run_resources(0, query)]
        # Filter by status by default
        assert {a.id for a in runs} == {"1", "3"}

        # If not added sometimes the profile collection is not updated
        await asyncio.sleep(0.01)

        profile_iter = system_profile_col.find({}).sort("ts", -1).limit(2)
        entry = await anext(profile_iter)
        if entry["op"] != "query":
            entry = await anext(profile_iter)
        assert entry["op"] == "query"
        assert entry["ns"] == "workflowai_test.task_runs"
        assert entry["planSummary"] == "IXSCAN { tenant: 1, task.id: 1, task.schema_id: 1, status: 1, created_at: -1 }"

    async def test_unique_version_ids(self, task_run_col: AsyncCollection, task_run_storage: MongoTaskRunStorage):
        hash_arg: dict[str, Any] = {
            "task_input_hash": "input1",
            "task_output_hash": "output1",
        }
        runs = [
            # Another tenant, should be ignored
            _task_run(tenant="another_tenant", cost_usd=110.75),
            # Another task schema, should be ignored
            _task_run(task_schema_id=3, cost_usd=102.0),
            _task_run(**hash_arg),
            _task_run(version_id="v2", **hash_arg),
            _task_run(version_id="v3", **hash_arg),
            # Not included because the input hash is different
            _task_run(version_id="v4", task_input_hash="1", task_output_hash="output1"),
            # Not included because the output hash is different
            _task_run(version_id="v5", task_input_hash="input1", task_output_hash="1"),
        ]

        await task_run_col.insert_many([dump_model(r) for r in runs])

        q = SerializableTaskRunQuery(
            task_id="task_id",
            task_schema_id=1,
            task_input_hashes={"input1"},
            task_output_hash="output1",
            unique_by={"version_id"},
            include_fields={"version_id"},
        )
        version_ids = {run.group.id async for run in task_run_storage.fetch_task_run_resources(1, q)}
        assert version_ids == {"group_hash", "v2", "v3"}

        q.group_ids = {"v2", "v3"}

        version_ids = {run.group.id async for run in task_run_storage.fetch_task_run_resources(1, q)}
        assert version_ids == {"v2", "v3"}


class TestFetchTaskRunResource:
    async def test_with_projection(self, task_run_storage: MongoTaskRunStorage, task_run_col: AsyncCollection) -> None:
        await task_run_col.insert_one(
            dump_model(_task_run(id="1", task_input_hash="2", task_output_hash="3")),
        )

        run = await task_run_storage.fetch_task_run_resource(
            _TASK_TUPLE,
            id="1",
            include={"task_schema_id", "task_input_hash", "task_output_hash"},
        )
        assert run.task_input_hash == "2"
        assert run.task_schema_id == 1
        assert run.task_output_hash == "3"

    async def test_with_group_properties(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ) -> None:
        await task_run_col.insert_one(dump_model(_task_run(id="1", group=TaskRunDocument.Group(properties={"a": 1}))))

        run = await task_run_storage.fetch_task_run_resource(
            _TASK_TUPLE,
            id="1",
            include={"group.properties"},
        )
        assert run.group.properties.model_dump(exclude_none=True) == {"a": 1}


class TestAggregateTaskMetadataFields:
    async def test_aggregate_task_metadata_fields(
        self,
        task_run_storage: MongoTaskRunStorage,
        task_run_col: AsyncCollection,
    ):
        await task_run_col.insert_one(dump_model(_task_run(id="1", metadata={"key1": "value1", "key2": "value2"})))

        fields = [f[0] async for f in task_run_storage.aggregate_task_metadata_fields(_TASK_TUPLE)]
        assert sorted(fields) == ["key1", "key2"]
