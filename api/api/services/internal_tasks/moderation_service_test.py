from unittest.mock import AsyncMock, patch

from api.services.internal_tasks.moderation_service import ModerationService
from api.tasks.moderation_task import ModerationOutput


async def test_handle_moderation_result_positive_with_iteration():
    tenant = "test_tenant"
    task_id = "test_task_id"
    user_and_org_str = "user@example.com"
    task_str = "https://www.example.com"
    iteration = 1
    term_breaching_category = ModerationOutput.TermBreachingCategory.SPAM
    result = ModerationOutput(is_breaching_terms=True, term_breaching_category=term_breaching_category)

    with patch(
        "api.services.internal_tasks.moderation_service.capture_content_moderation_error",
        new_callable=AsyncMock,
    ) as mock_capture_content_moderation_error:
        await ModerationService._handle_task_version_moderation_result(  # pyright: ignore[reportPrivateUsage]
            tenant=tenant,
            task_id=task_id,
            user_and_org_str=user_and_org_str,
            task_str=task_str,
            iteration=iteration,
            result=result,
        )

        expected_message = "user@example.com created an iteration that is breaching terms (SPAM): https://www.example.com (iteration:1)"

        assert mock_capture_content_moderation_error.call_args[0][0].args[0] == expected_message
        assert mock_capture_content_moderation_error.call_args[0][1] == tenant
        assert mock_capture_content_moderation_error.call_args[0][2] == task_id


async def test_handle_moderation_result_positive_without_iteration():
    tenant = "test_tenant"
    task_id = "test_task_id"
    user_and_org_str = "user@example.com"
    task_str = "https://www.example.com"
    iteration = None
    term_breaching_category = ModerationOutput.TermBreachingCategory.SPAM
    result = ModerationOutput(is_breaching_terms=True, term_breaching_category=term_breaching_category)

    with patch(
        "api.services.internal_tasks.moderation_service.capture_content_moderation_error",
        new_callable=AsyncMock,
    ) as mock_capture_content_moderation_error:
        await ModerationService._handle_task_version_moderation_result(  # pyright: ignore[reportPrivateUsage]
            tenant=tenant,
            task_id=task_id,
            user_and_org_str=user_and_org_str,
            task_str=task_str,
            iteration=iteration,
            result=result,
        )

        expected_message = "user@example.com created a task that is breaching terms (SPAM): https://www.example.com"

        assert mock_capture_content_moderation_error.call_args[0][0].args[0] == expected_message
        assert mock_capture_content_moderation_error.call_args[0][1] == tenant
        assert mock_capture_content_moderation_error.call_args[0][2] == task_id


async def test_handle_moderation_result_negative():
    tenant = "test_tenant"
    task_id = "test_task_id"
    user_and_org_str = "user@example.com"
    task_str = "Sample Task"
    iteration = 1
    result = ModerationOutput(is_breaching_terms=False, term_breaching_category=None)

    with patch(
        "api.services.internal_tasks.moderation_service.capture_content_moderation_error",
        new_callable=AsyncMock,
    ) as mock_capture_content_moderation_error:
        await ModerationService._handle_task_version_moderation_result(  # pyright: ignore[reportPrivateUsage]
            tenant=tenant,
            task_id=task_id,
            user_and_org_str=user_and_org_str,
            task_str=task_str,
            iteration=iteration,
            result=result,
        )

        mock_capture_content_moderation_error.assert_not_awaited()


async def test_handle_task_run_moderation_result_positive():
    tenant = "test_tenant"
    task_id = "test_task_id"
    user_and_org_str = "user@example.com"
    task_run_str = "https://www.example.com"
    term_breaching_category = ModerationOutput.TermBreachingCategory.SPAM
    result = ModerationOutput(is_breaching_terms=True, term_breaching_category=term_breaching_category)

    with patch(
        "api.services.internal_tasks.moderation_service.capture_content_moderation_error",
        new_callable=AsyncMock,
    ) as mock_capture_content_moderation_error:
        await ModerationService._handle_task_run_moderation_result(  # pyright: ignore[reportPrivateUsage]
            tenant=tenant,
            task_id=task_id,
            user_and_org_str=user_and_org_str,
            task_run_str=task_run_str,
            result=result,
        )

        expected_message = "user@example.com created a task run that is breaching terms (SPAM): https://www.example.com"

        assert mock_capture_content_moderation_error.call_args[0][0].args[0] == expected_message
        assert mock_capture_content_moderation_error.call_args[0][1] == tenant
        assert mock_capture_content_moderation_error.call_args[0][2] == task_id


async def test_handle_task_run_moderation_result_negative():
    tenant = "test_tenant"
    task_id = "test_task_id"
    user_and_org_str = "user@example.com"
    task_run_str = "Sample Task Run"
    result = ModerationOutput(is_breaching_terms=False, term_breaching_category=None)

    with patch(
        "api.services.internal_tasks.moderation_service.capture_content_moderation_error",
        new_callable=AsyncMock,
    ) as mock_capture_content_moderation_error:
        await ModerationService._handle_task_run_moderation_result(  # pyright: ignore[reportPrivateUsage]
            tenant=tenant,
            task_id=task_id,
            user_and_org_str=user_and_org_str,
            task_run_str=task_run_str,
            result=result,
        )

        mock_capture_content_moderation_error.assert_not_awaited()
