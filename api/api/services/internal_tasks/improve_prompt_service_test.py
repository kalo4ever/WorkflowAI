from unittest.mock import AsyncMock, Mock, patch

import pytest
from workflowai import Run

from api.services.internal_tasks.improve_prompt_service import ImprovePromptService
from api.tasks.chat_task_schema_generation.apply_field_updates import InputFieldUpdate, OutputFieldUpdate
from api.tasks.improve_prompt import ImprovePromptAgentOutput
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_variant import SerializableTaskVariant
from tests import models
from tests.utils import mock_aiter


def _improve_task_output(
    improved_prompt: str = "This is an improved prompt",
    field_updates: list[OutputFieldUpdate] | None = None,
    input_field_updates: list[InputFieldUpdate] | None = None,
):
    return ImprovePromptAgentOutput(
        improved_prompt=improved_prompt,
        changelog=["Minor tweaks"],
        output_field_updates=field_updates,
        input_field_updates=input_field_updates,
    )


def _run(output: ImprovePromptAgentOutput):
    return Run(
        id="1",
        agent_id="1",
        schema_id=1,
        output=output,
    )


@pytest.fixture
def improve_prompt_service(mock_storage: Mock):
    return ImprovePromptService(mock_storage)


@pytest.fixture
def patched_logger(improve_prompt_service: ImprovePromptService):
    with patch.object(improve_prompt_service, "_logger") as mock:
        yield mock


@pytest.fixture
def patched_improve_prompt_run():
    with patch(
        "api.services.internal_tasks.improve_prompt_service.run_improve_prompt_agent",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


@pytest.fixture
def patched_improve_prompt_stream():
    with patch("api.services.internal_tasks.improve_prompt_service.run_improve_prompt_agent", autospec=True) as mock:
        mock.stream = Mock()
        yield mock.stream


class TestImprovePrompt:
    @pytest.fixture(autouse=True)
    def fetched_properties(self, mock_storage: Mock):
        properties = TaskGroupProperties.model_validate(
            {
                "model": "model",
                "instructions": "You are a helpful assistant.",
                "task_variant_id": "1",
            },
        )
        mock_storage.task_groups.get_task_group_by_id.return_value = TaskGroup(
            properties=properties,
        )
        return properties

    @pytest.fixture(autouse=True)
    def fetched_variant(self, mock_storage: Mock):
        task_variant = models.task_variant(
            input_schema={
                "type": "object",
                "properties": {
                    "input_field": {"type": "string"},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                },
            },
        )
        mock_storage.task_version_resource_by_id.return_value = task_variant
        return task_variant

    @pytest.fixture(autouse=True)
    def fetched_run(self, mock_storage: Mock):
        task_run = models.task_run_ser(
            task_input={"input_field": "test"},
            task_output={"result": "test"},
        )
        mock_storage.task_runs.fetch_task_run_resource.return_value = task_run
        return task_run

    async def test_run_schema_updated(
        self,
        patched_improve_prompt_run: Mock,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
        fetched_variant: SerializableTaskVariant,
    ):
        patched_improve_prompt_run.return_value = _improve_task_output(
            field_updates=[
                OutputFieldUpdate(
                    keypath="result",
                    updated_description="A test string field",
                    updated_examples=["example1", "example2"],
                ),
            ],
            input_field_updates=[
                InputFieldUpdate(
                    keypath="input_field",
                    updated_description="A test input field",
                ),
            ],
        )

        mock_storage.store_task_resource.return_value = fetched_variant.model_copy(update={"id": "new_id"}), True

        # Act
        result = await improve_prompt_service.run(("", 1), "1", "This is a user evaluation.")

        # Assert
        # Test that we stored a new task variant, since there are schema updates
        mock_storage.store_task_resource.assert_awaited_once()
        created_variant: SerializableTaskVariant = mock_storage.store_task_resource.call_args.args[0]
        assert created_variant.input_schema.json_schema == {
            "type": "object",
            "properties": {
                "input_field": {
                    "type": "string",
                    "description": "A test input field",
                },
            },
        }
        assert created_variant.output_schema.json_schema == {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "A test string field",
                    "examples": [
                        "example1",
                        "example2",
                    ],
                },
            },
        }

        assert result == (
            TaskGroupProperties.model_validate(
                {
                    "model": "model",
                    "instructions": "This is an improved prompt",
                    "task_variant_id": "new_id",
                },
            ),
            ["Minor tweaks"],
        )
        # Check that the improve prompt task was called with the correct input
        patched_improve_prompt_run.assert_awaited_once()
        task_input = patched_improve_prompt_run.call_args.args[0]
        assert task_input.agent_run.user_evaluation == "This is a user evaluation."

    async def test_run_no_field_updates(
        self,
        patched_improve_prompt_run: Mock,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
    ):
        patched_improve_prompt_run.return_value = _improve_task_output()

        # Act
        result = await improve_prompt_service.run(("", 1), "1", "This is a user evaluation.")

        # Assert
        # Test that we did not store a new task variant, since there is no 'improved_output_schema'
        mock_storage.store_task_resource.assert_not_called()
        assert result == (
            TaskGroupProperties.model_validate(
                {
                    "model": "model",
                    "instructions": "This is an improved prompt",
                    "task_variant_id": "1",
                },
            ),
            ["Minor tweaks"],
        )

        mock_storage.store_task_resource.assert_not_called()

    async def test_stream_schema_updated(
        self,
        patched_improve_prompt_stream: Mock,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
        fetched_variant: SerializableTaskVariant,
    ):
        patched_improve_prompt_stream.return_value = mock_aiter(
            _run(_improve_task_output(improved_prompt="This is an")),
            _run(_improve_task_output(improved_prompt="This is an improved prompt")),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[],
                    input_field_updates=[],
                ),
            ),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[
                        OutputFieldUpdate(
                            keypath="result",
                        ),
                    ],
                    input_field_updates=[
                        InputFieldUpdate(
                            keypath="input_field",
                        ),
                    ],
                ),
            ),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[
                        OutputFieldUpdate(
                            keypath="result",
                            updated_description="A test string field",
                            updated_examples=["example1", "example2"],
                        ),
                    ],
                    input_field_updates=[
                        InputFieldUpdate(
                            keypath="input_field",
                            updated_description="A test input field",
                        ),
                    ],
                ),
            ),
        )

        mock_storage.store_task_resource.return_value = fetched_variant.model_copy(update={"id": "new_id"}), True

        # Act

        chunks = [
            c
            async for c in improve_prompt_service.stream(
                task_tuple=("", 1),
                run_id="1",
                user_evaluation="This is a user evaluation.",
            )
        ]
        assert len(chunks) == 6  # 5 + 1 when the task variant is updated

        assert chunks[0][0].instructions == "This is an"
        assert chunks[0][0] != "new_id", "sanity"
        assert chunks[-1][0].task_variant_id == "new_id"

        # Test that we stored a new task variant, since there are schema updates
        mock_storage.store_task_resource.assert_awaited_once()
        created_variant: SerializableTaskVariant = mock_storage.store_task_resource.call_args.args[0]
        assert created_variant.input_schema.json_schema == {
            "type": "object",
            "properties": {
                "input_field": {
                    "type": "string",
                    "description": "A test input field",
                },
            },
        }
        assert created_variant.output_schema.json_schema == {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "A test string field",
                    "examples": [
                        "example1",
                        "example2",
                    ],
                },
            },
        }

    async def test_stream_no_field_updates(
        self,
        patched_improve_prompt_stream: Mock,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
    ):
        patched_improve_prompt_stream.return_value = mock_aiter(
            _run(_improve_task_output(improved_prompt="This is an")),
            _run(_improve_task_output(improved_prompt="This is an improved prompt")),
        )

        # Act

        chunks = [
            c
            async for c in improve_prompt_service.stream(
                task_tuple=("", 1),
                run_id="1",
                user_evaluation="This is a user evaluation.",
            )
        ]
        assert len(chunks) == 2

        # Assert
        mock_storage.store_task_resource.assert_not_called()
        patched_improve_prompt_stream.assert_called_once()

    async def test_run_invalid_field_updates(
        self,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
        patched_improve_prompt_run: Mock,
        patched_logger: Mock,
        fetched_properties: TaskGroupProperties,
    ):
        """Test that we fail silently when the updated fields do not exist in the task variant"""
        # The field updates are not valid since the fields do not exist
        patched_improve_prompt_run.return_value = _improve_task_output(
            field_updates=[
                OutputFieldUpdate(
                    keypath="result1",
                    updated_description="A test string field",
                    updated_examples=["example1", "example2"],
                ),
            ],
            input_field_updates=[
                InputFieldUpdate(
                    keypath="input_field1",
                    updated_description="A test input field",
                ),
            ],
        )

        # In which case the run should succeed but a new task variant should not be created
        result = await improve_prompt_service.run(
            task_tuple=("", 1),
            run_id="1",
            user_evaluation="This is a user evaluation.",
        )

        assert result == (
            fetched_properties.model_copy(update={"instructions": "This is an improved prompt"}),
            ["Minor tweaks"],
        )

        mock_storage.store_task_resource.assert_not_called()
        patched_logger.exception.assert_called_once()
        assert patched_logger.exception.call_args.args[0] == "Error handling improved output schema"

    async def test_stream_invalid_field_updates(
        self,
        improve_prompt_service: ImprovePromptService,
        mock_storage: Mock,
        patched_improve_prompt_stream: Mock,
        patched_logger: Mock,
    ):
        """Test that we fail silently on streams when the updated fields do not exist in the task variant"""
        # The field updates are not valid since the fields do not exist
        patched_improve_prompt_stream.return_value = mock_aiter(
            _run(_improve_task_output(improved_prompt="This is an")),
            _run(_improve_task_output(improved_prompt="This is an improved prompt")),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[],
                    input_field_updates=[],
                ),
            ),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[
                        OutputFieldUpdate(
                            keypath="result1",
                        ),
                    ],
                    input_field_updates=[
                        InputFieldUpdate(
                            keypath="input_field1",
                            updated_description="A test input field",
                        ),
                    ],
                ),
            ),
            _run(
                _improve_task_output(
                    improved_prompt="This is an improved prompt",
                    field_updates=[
                        OutputFieldUpdate(
                            keypath="result1",
                            updated_description="A test string field",
                            updated_examples=["example1", "example2"],
                        ),
                    ],
                    input_field_updates=[
                        InputFieldUpdate(
                            keypath="input_field1",
                            updated_description="A test input field",
                        ),
                    ],
                ),
            ),
        )

        # In which case the run should succeed but a new task variant should not be created

        chunks = [
            c
            async for c in improve_prompt_service.stream(
                task_tuple=("", 1),
                run_id="1",
                user_evaluation="This is a user evaluation.",
            )
        ]
        assert len(chunks) == 5

        mock_storage.store_task_resource.assert_not_called()
        patched_logger.exception.assert_called_once()
        assert patched_logger.exception.call_args.args[0] == "Error handling improved output schema"
