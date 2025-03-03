from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.jobs.run_created_jobs import (
    _should_run_task_run_moderation,  # pyright: ignore[reportPrivateUsage]
    run_task_run_moderation,
)


async def test_run_task_run_moderation_skips_when_should_not_run() -> None:
    with patch("api.jobs.run_created_jobs._should_run_task_run_moderation", return_value=False):
        internal_service_mock = AsyncMock()
        with patch("api.jobs.run_created_jobs.InternalTasksServiceDep", return_value=internal_service_mock):
            await run_task_run_moderation(Mock(), internal_service_mock)

            # Verify that the moderation process was not called
            internal_service_mock.moderation.run_task_run_moderation_process.assert_not_called()


async def test_run_task_run_moderation_should_run() -> None:
    with patch("api.jobs.run_created_jobs._should_run_task_run_moderation", return_value=True):
        internal_service_mock = AsyncMock()
        with patch("api.jobs.run_created_jobs.InternalTasksServiceDep", return_value=internal_service_mock):
            await run_task_run_moderation(Mock(), internal_service_mock)

            # Verify that the moderation process was not called
            internal_service_mock.moderation.run_task_run_moderation_process.assert_called_once()


def test_should_run_task_run_moderation_sampling_rate() -> None:
    # Run the function 10000 times to get a statistically significant sample
    runs = 10000
    true_count = sum(_should_run_task_run_moderation() for _ in range(runs))

    # Calculate the actual percentage
    actual_rate = true_count / runs

    # We expect 1% (0.01) with some margin of error
    # Using a tolerance of ±0.4% to account for random variation
    assert pytest.approx(actual_rate, abs=0.004) == 0.01  # pyright: ignore [reportUnknownMemberType]
