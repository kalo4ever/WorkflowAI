from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun.api import FrozenDateTimeFactory

from api.services.reviews import (
    ReviewsService,
    _InternalTasks,  # pyright: ignore [reportPrivateUsage]
)
from core.domain.agent_run import TaskRunIO
from core.domain.events import RecomputeReviewBenchmarkEvent
from core.domain.input_evaluation import InputEvaluation
from core.domain.review import Review, ReviewOutcome
from core.domain.task_evaluation import TaskEvaluation
from core.domain.users import UserIdentifier
from core.evaluators.abstract_evaluator import AbstractEvaluator
from core.storage.review_benchmark_storage import RunReviewAggregateWithIteration
from core.storage.task_run_storage import RunAggregate
from core.utils.fields import datetime_factory
from tests.models import task_variant
from tests.utils import mock_aiter


@pytest.fixture
def mock_internal_tasks():
    return AsyncMock(spec=_InternalTasks)


@pytest.fixture
def reviews_service(mock_storage: Mock, mock_internal_tasks: Mock, mock_event_router: Mock):
    return ReviewsService(mock_storage, mock_internal_tasks, mock_event_router)


def _run_agg(eval_hashes: list[str] = [], **kwargs: Any):
    raw = RunAggregate(
        eval_hashes=eval_hashes,
        total_run_count=1,
        failed_run_count=0,
        average_cost_usd=0,
        average_duration_seconds=0,
    )
    return cast(RunAggregate, {**raw, **kwargs})


def _review_agg(iteration: int = 1, **kwargs: Any):
    raw = RunReviewAggregateWithIteration(
        iteration=iteration,
        average_cost_usd=0,
        average_duration_seconds=0,
        total_run_count=1,
        failed_run_count=0,
        in_progress_review_count=0,
        positive_review_count=0,
        positive_user_review_count=0,
        negative_review_count=0,
        negative_user_review_count=0,
        unsure_review_count=0,
    )
    return cast(RunReviewAggregateWithIteration, {**raw, **kwargs})


def _review(eval_hash: str = "", user: bool = False, outcome: ReviewOutcome = "positive", **kwargs: Any):
    r = Review(
        task_id="task_id",
        task_schema_id=1,
        id="review_id",
        task_input_hash="input_hash",
        task_output_hash="output_hash",
        outcome=outcome,
        status="completed",
        reviewer=Review.AIReviewer() if not user else Review.UserReviewer(),
        eval_hash=eval_hash,
    )
    return r.model_copy(update=kwargs)


class TestRecomputeReviewBenchmark:
    async def test_skipped(self, reviews_service: ReviewsService, mock_storage: Mock):
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = set()

        await reviews_service.recompute_review_benchmark(
            task_id="task_id",
            task_schema_id=1,
        )

        mock_storage.review_benchmarks.update_benchmark.assert_not_called()

    async def test_find_no_input_hashes_no_iterations(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        frozen_time: FrozenDateTimeFactory,
    ):
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = {1, 2}
        mock_storage.get_task_tuple.return_value = ("task_id", 1)
        mock_storage.task_groups.map_iterations.return_value = {2: "v2", 1: "v1"}

        mock_storage.reviews.find_unique_input_hashes.return_value = {"a", "b"}
        mock_storage.task_runs.aggregate_runs.return_value = {
            "v1": _run_agg(["e1", "e2"]),
            "v2": _run_agg(["e1", "e3"], total_run_count=2, failed_run_count=1),
        }
        mock_storage.reviews.reviews_for_eval_hashes.return_value = mock_aiter(
            # 2 reviews
            _review(eval_hash="e1", user=True),  # positive user review for v1 and v2
            _review(eval_hash="e2"),  # positive ai review for v1
            _review(eval_hash="e3", outcome="negative"),  # negative AI review for v2
        )

        await reviews_service.recompute_review_benchmark(
            task_id="task_id",
            task_schema_id=1,
        )

        mock_storage.review_benchmarks.update_benchmark.assert_awaited_once_with(
            "task_id",
            1,
            [
                _review_agg(
                    1,
                    version_id="v1",
                    positive_review_count=2,
                    positive_user_review_count=1,
                ),
                _review_agg(
                    2,
                    version_id="v2",
                    total_run_count=2,
                    positive_review_count=1,
                    positive_user_review_count=1,
                    failed_run_count=1,
                    negative_review_count=1,
                ),
            ],
            datetime_factory(),
        )

        mock_storage.task_runs.aggregate_runs.assert_called_once_with(
            ("task_id", 1),
            1,
            {"a", "b"},
            {"v1", "v2"},
        )
        mock_storage.task_groups.map_iterations.assert_awaited_once_with("task_id", 1, {1, 2})

    async def test_find_with_iterations(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        frozen_time: FrozenDateTimeFactory,
    ):
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = {1, 2}
        mock_storage.get_task_tuple.return_value = ("task_id", 1)
        mock_storage.task_groups.map_iterations.return_value = {2: "v2"}
        mock_storage.reviews.find_unique_input_hashes.return_value = {"a", "b"}
        mock_storage.task_runs.aggregate_runs.return_value = {
            "v2": _run_agg(["e1"]),
        }
        mock_storage.reviews.reviews_for_eval_hashes.return_value = mock_aiter(
            _review(eval_hash="e1", user=True),  # positive user review for v2
        )

        await reviews_service.recompute_review_benchmark(
            task_id="task_id",
            task_schema_id=1,
            iterations={2},
        )
        mock_storage.task_groups.map_iterations.assert_awaited_once_with("task_id", 1, {2})

        mock_storage.review_benchmarks.update_benchmark.assert_awaited_once_with(
            "task_id",
            1,
            [_review_agg(2, version_id="v2", positive_review_count=1, positive_user_review_count=1)],
            datetime_factory(),
        )
        mock_storage.task_runs.aggregate_runs.assert_called_once_with(
            ("task_id", 1),
            1,
            {"a", "b"},
            {"v2"},
        )
        mock_storage.task_groups.map_iterations.assert_awaited_once_with("task_id", 1, {2})

    async def test_complete_run(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        frozen_time: FrozenDateTimeFactory,
    ):
        mock_storage.get_task_tuple.return_value = ("task_id", 1)
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = {1, 2}
        mock_storage.reviews.find_unique_input_hashes.return_value = {"a", "b"}
        mock_storage.task_groups.map_iterations.return_value = {1: "v1"}
        mock_storage.task_runs.aggregate_runs.return_value = {
            "v1": _run_agg(["e1", "e2"]),
        }
        mock_storage.reviews.reviews_for_eval_hashes.return_value = mock_aiter(
            _review(eval_hash="e1", user=True),
        )

        await reviews_service.recompute_review_benchmark(
            task_id="task_id",
            task_schema_id=1,
            iterations={1},
            run_id="run_id",
        )

        mock_storage.review_benchmarks.complete_run.assert_awaited_once_with("task_id", 1, 1, "run_id")
        mock_storage.review_benchmarks.update_benchmark.assert_awaited_once()
        mock_storage.task_runs.aggregate_runs.assert_called_once()
        mock_storage.task_groups.map_iterations.assert_awaited_once_with("task_id", 1, {1})


class TestTriggerRunsForBenchmark:
    async def test_no_iterations(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = set()

        await reviews_service.trigger_runs_for_benchmark(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            is_first_review=True,
            run_id="blah",
        )
        mock_storage.review_benchmarks.get_benchmark_versions.assert_awaited_once_with(
            "task_id",
            1,
        )
        mock_storage.task_runs.fetch_task_run_resource.assert_not_called()

        mock_event_router.assert_not_called()

    async def test_with_iterations(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        mock_storage.review_benchmarks.get_benchmark_versions.return_value = {1, 2}

        await reviews_service.trigger_runs_for_benchmark(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            is_first_review=True,
            run_id=None,
        )

        mock_storage.review_benchmarks.get_benchmark_versions.assert_awaited_once_with(
            "task_id",
            1,
        )

        assert mock_event_router.call_count == 2


class TestEvaluateRun:
    async def test_successful_evaluation(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        mock_evaluator = Mock(spec=AbstractEvaluator)
        mock_run = Mock(spec=TaskRunIO)
        # Setup evaluator mock to return a score
        mock_evaluator.evaluate.return_value = TaskEvaluation(
            score=1,
            evaluator=TaskEvaluation.Evaluator(
                name="evaluator",
                id="",
                properties={},
            ),
            positive_aspects=["good1", "good2"],
            negative_aspects=["bad1"],
        )
        review = _review()

        # Call the method
        await reviews_service._evaluate_run(mock_evaluator, mock_run, review)  # pyright: ignore [reportPrivateUsage]

        # Verify evaluator was called
        mock_evaluator.evaluate.assert_awaited_once_with(mock_run, example=None)

        # Verify review was completed
        mock_storage.reviews.complete_review.assert_awaited_once()

        # Verify event was sent
        mock_event_router.assert_called_once()
        event = mock_event_router.call_args[0][0]
        assert event.review_id == review.id

    async def test_failed_evaluation(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        mock_evaluator = Mock(spec=AbstractEvaluator)
        mock_run = Mock(spec=TaskRunIO)
        review = _review()

        # Setup evaluator mock to raise an exception
        mock_evaluator.evaluate.side_effect = ValueError("Evaluation failed")

        # Call the method
        await reviews_service._evaluate_run(mock_evaluator, mock_run, review)  # pyright: ignore [reportPrivateUsage]

        # Verify evaluator was called
        mock_evaluator.evaluate.assert_awaited_once_with(mock_run, example=None)

        # Verify review was failed
        mock_storage.reviews.fail_review.assert_awaited_once_with(review.id)

        # Verify event was sent with review_id=None since the review no longer exists
        mock_event_router.assert_called_once()
        event = mock_event_router.call_args[0][0]
        assert event.review_id is None


class TestUpdateInputEvaluation:
    async def test_update_correct_outputs(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
    ):
        mock_storage.get_task_tuple.return_value = ("task_id", 1)
        mock_run = Mock(spec=TaskRunIO)
        mock_run.task_input = {"name": "John"}

        mock_storage.input_evaluations.get_latest_input_evaluation.return_value = InputEvaluation(
            id="",
            task_input_hash="hash",
            correct_outputs=[{"greeting": "Hello James!"}],
            incorrect_outputs=[],
            evaluation_instruction=None,
        )

        async def _create_input_evaluation(**kwargs: Any):
            return kwargs["input_evaluation"]

        mock_storage.input_evaluations.create_input_evaluation.side_effect = _create_input_evaluation

        mock_storage.task_runs.fetch_task_run_resources.return_value = mock_aiter(mock_run)

        out = await reviews_service.update_input_evaluation(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            instructions=None,
            correct_outputs=ReviewsService.OutputListUpdate(add={"greeting": "Hello John!"}, remove=None),
            incorrect_outputs=ReviewsService.OutputListUpdate(add=None, remove=None),
            user=UserIdentifier(user_email="user@example.com"),
        )

        assert out.correct_outputs == [{"greeting": "Hello James!"}, {"greeting": "Hello John!"}]
        assert out.incorrect_outputs == []

        mock_storage.input_evaluations.create_input_evaluation.assert_awaited_once()

    async def test_empty_instructions(self, reviews_service: ReviewsService, mock_storage: Mock):
        mock_storage.get_task_tuple.return_value = ("task_id", 1)
        mock_storage.input_evaluations.get_latest_input_evaluation.return_value = InputEvaluation(
            id="1",
            task_input_hash="hash",
            correct_outputs=[{"greeting": "Hello James!"}],
            incorrect_outputs=[],
            evaluation_instruction="hello",
        )

        async def _create_input_evaluation(**kwargs: Any):
            created = kwargs["input_evaluation"]
            assert isinstance(created, InputEvaluation)
            assert created.id == ""
            assert created.evaluation_instruction == ""
            return created.model_copy(update={"id": "2"})

        mock_storage.input_evaluations.create_input_evaluation.side_effect = _create_input_evaluation

        out = await reviews_service.update_input_evaluation(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            instructions="",
            correct_outputs=ReviewsService.OutputListUpdate(None, None),
            incorrect_outputs=ReviewsService.OutputListUpdate(None, None),
            user=UserIdentifier(user_email="user@example.com"),
        )

        assert out.evaluation_instructions == ""
        assert out.correct_outputs == [{"greeting": "Hello James!"}]
        assert out.incorrect_outputs == []

        mock_storage.input_evaluations.create_input_evaluation.assert_awaited_once()


class TestListReviewedInputs:
    async def test_no_input_evaluations(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
    ):
        mock_storage.input_evaluations.list_input_evaluations_unique_by_hash.return_value = mock_aiter()

        assert await reviews_service.list_reviewed_inputs(("task_id", 0), 1) == []
        mock_storage.task_runs.fetch_task_run_resources.assert_not_called()


class TestEvaluateRunsByHashIfNeeded:
    async def test_existing_user_review(
        self,
        reviews_service: ReviewsService,
        mock_storage: Mock,
        mock_event_router: Mock,
    ):
        mock_storage.task_variants.get_latest_task_variant.return_value = task_variant()
        mock_storage.reviews.get_review_by_hash.return_value = _review(reviewer=Review.UserReviewer())

        await reviews_service.evaluate_runs_by_hash_if_needed(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            task_output_hash="hash",
            run_id="run_id",
            version_id="version_id",
            iteration=1,
            run_failed=False,
        )

        mock_event_router.assert_called_once_with(
            RecomputeReviewBenchmarkEvent(
                task_id="task_id",
                task_schema_id=1,
                run_id="run_id",
                iterations={1},
            ),
        )

        mock_storage.reviews.get_review_by_hash.assert_called_once_with(
            task_id="task_id",
            task_schema_id=1,
            task_input_hash="hash",
            task_output_hash="hash",
            reviewer="user",
            include={"outcome", "status"},
        )
