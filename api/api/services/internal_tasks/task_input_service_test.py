from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.services.internal_tasks.task_input_service import TaskInputService
from api.tasks.task_input_import_task import TaskInputImportTaskInput, TaskInputImportTaskOutput
from core.domain.task_variant import SerializableTaskVariant
from tests.models import task_variant
from tests.utils import mock_aiter


@pytest.fixture
def task_input_service():
    return TaskInputService()


@pytest.fixture
def mock_task():
    return task_variant(
        name="MockTask",
        input_schema={
            "type": "object",
            "properties": {"key": {"type": "string"}, "key2": {"type": "string"}},
        },
    )


@pytest.fixture(autouse=True)
def patched_validate_input():
    def validate_input(x: Any, partial: bool = False) -> Any:
        return x

    with patch(
        "core.domain.task_variant.SerializableTaskVariant.validate_input",
        side_effect=validate_input,
    ) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_task_input_import():
    with patch("api.services.internal_tasks.task_input_service.task_input_import", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_stream_task_input_import():
    with patch(
        "api.services.internal_tasks.task_input_service.stream_task_inputs_import_task",
    ) as mock:
        yield mock


class TestTaskInputService:
    async def test_import_input_not_stream(
        self,
        task_input_service: Mock,
        mock_task_input_import: Mock,
        mock_task: SerializableTaskVariant,
    ):
        mock_task_input_import.return_value = TaskInputImportTaskOutput(
            extracted_task_inputs=[{"key": "value1", "key2": "value2"}, {"key": "value3", "key2": "value4"}],
        )

        result = await task_input_service.import_input(
            task=mock_task,
            inputs_text="raw input data",
        )

        assert result == [{"key": "value1", "key2": "value2"}, {"key": "value3", "key2": "value4"}]
        mock_task_input_import.assert_called_once()
        call_args = mock_task_input_import.call_args[0][0]
        assert call_args == TaskInputImportTaskInput(
            task_name="MockTask",
            input_json_schema=mock_task.input_schema.json_schema,
            raw_input_data="raw input data",
        )

    async def test_import_input_stream(
        self,
        task_input_service: Mock,
        mock_stream_task_input_import: Mock,
        mock_task: SerializableTaskVariant,
    ):
        mock_stream_task_input_import.return_value = mock_aiter(
            TaskInputImportTaskOutput(extracted_task_inputs=[{"key": "value1"}]),
            TaskInputImportTaskOutput(extracted_task_inputs=[{"key": "value1", "key2": "value2"}]),
            TaskInputImportTaskOutput(
                extracted_task_inputs=[
                    {"key": "value1", "key2": "value2"},
                    {"key": "value3", "key2": "value4"},
                ],
            ),
            TaskInputImportTaskOutput(
                extracted_task_inputs=[
                    {"key": "value1", "key2": "value2"},
                    {"key": "value3", "key2": "value4"},
                    {"key": "value5", "key2": "value6"},
                ],
            ),
        )

        stream = task_input_service.stream_import_input(
            task=mock_task,
            inputs_text="raw input data",
        )

        result = [chunk async for chunk in stream]
        assert result == [
            (0, {"key": "value1"}),
            (0, {"key": "value1", "key2": "value2"}),
            (0, {"key": "value1", "key2": "value2"}),
            (1, {"key": "value3", "key2": "value4"}),
            (1, {"key": "value3", "key2": "value4"}),
            (2, {"key": "value5", "key2": "value6"}),
        ]

        mock_stream_task_input_import.assert_called_once()
        call_args = mock_stream_task_input_import.call_args[0][0]
        assert call_args == TaskInputImportTaskInput(
            task_name="MockTask",
            input_json_schema=mock_task.input_schema.json_schema,
            raw_input_data="raw input data",
        )

    async def test_import_input_stream_empty_chunk(
        self,
        task_input_service: Mock,
        mock_stream_task_input_import: Mock,
        mock_task: SerializableTaskVariant,
    ):
        mock_stream_task_input_import.return_value = mock_aiter(
            TaskInputImportTaskOutput(extracted_task_inputs=[]),
            TaskInputImportTaskOutput(extracted_task_inputs=[{"key": "value1"}]),
            TaskInputImportTaskOutput(extracted_task_inputs=[{"key": "value1"}, {"key": "value2"}]),
        )

        stream = task_input_service.stream_import_input(
            task=mock_task,
            inputs_text="raw input data",
        )

        result = [chunk async for chunk in stream]
        assert result == [
            (0, {"key": "value1"}),
            (0, {"key": "value1"}),
            (1, {"key": "value2"}),
        ]

        mock_stream_task_input_import.assert_called_once()
