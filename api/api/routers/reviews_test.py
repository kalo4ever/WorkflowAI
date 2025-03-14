from unittest.mock import Mock

from httpx import AsyncClient

from api.routers.reviews import ReviewBenchmark
from core.domain.review_benchmark import ReviewBenchmark as DomainReviewBenchmark
from core.domain.task_group_properties import TaskGroupProperties
from tests.models import task_run_ser


class TestVersionResult:
    def test_from_domain(self):
        d = DomainReviewBenchmark.VersionAggregation(
            iteration=1,
            properties=TaskGroupProperties(model=""),
            positive_review_count=1,
            positive_user_review_count=2,
            negative_review_count=3,
            negative_user_review_count=4,
            unsure_review_count=5,
            in_progress_review_count=6,
            total_run_count=7,
            run_failed_count=8,
            run_in_progress_count=1,
            average_cost_usd=None,
            average_duration_seconds=None,
        )
        v = ReviewBenchmark.VersionResult.from_domain(d)
        assert v.iteration == d.iteration

        assert v.positive_review_count == 1
        assert v.positive_user_review_count == 2
        assert v.negative_review_count == 3
        assert v.negative_user_review_count == 4
        assert v.unsure_review_count == 5
        assert v.in_progress_review_count == 7


class TestListReviews:
    async def test_failure(
        self,
        mock_reviews_service: Mock,
        mock_storage: Mock,
        test_api_client: AsyncClient,
    ):
        # On failed runs, we insert a fake review
        mock_storage.task_runs.fetch_task_run_resource.return_value = task_run_ser(status="failure")

        response = await test_api_client.get("/_/agents/evaluate-output/runs/1/reviews")
        mock_reviews_service.list_reviews.assert_called_once_with(
            task_id="evaluate-output",
            task_schema_id=1,
            task_input_hash="input_hash",
            task_output_hash="output_hash",
        )

        assert response.status_code == 200


class TestCreateReview:
    async def test_on_failed_run(
        self,
        test_api_client: AsyncClient,
        mock_storage: Mock,
    ):
        # On failed runs, we insert a fake review
        mock_storage.task_runs.fetch_task_run_resource.return_value = task_run_ser(status="failure")

        response = await test_api_client.post(
            "/_/agents/evaluate-output/runs/1/reviews",
            json={
                "outcome": "negative",
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "error": {
                "code": "bad_request",
                "message": "Cannot review a failed run",
                "status_code": 400,
            },
        }
