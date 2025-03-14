import asyncio
from datetime import datetime, timezone
from typing import Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.services.internal_tasks.internal_tasks_service import (
    AUDIO_TRANSCRIPTION_MODEL,
    InternalTasksService,
)
from api.services.tasks import AgentSummary
from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import (
    AgentBuilderInput,
    AgentBuilderOutput,
    AgentSchema,
    AgentSchemaJson,
    EnumFieldConfig,
    InputArrayFieldConfig,
    InputGenericFieldConfig,
    InputObjectFieldConfig,
    InputSchemaFieldType,
    OutputObjectFieldConfig,
    OutputStringFieldConfig,
)
from api.tasks.extract_company_info_from_domain_task import ExtractCompanyInfoFromDomainTaskOutput, Product
from api.tasks.generate_changelog import (
    GenerateChangelogFromPropertiesTaskInput,
    GenerateChangelogFromPropertiesTaskOutput,
    Properties,
    Schema,
    TaskGroupWithSchema,
)
from api.tasks.input_generation_instructions_agent import InputGenerationInstructionsOutput
from api.tasks.task_description_generation.task_description_generation_task import (
    TaskDescriptionGenerationTaskInput,
    TaskDescriptionGenerationTaskOutput,
)
from api.tasks.task_instruction_generation.task_instructions_generation_task import (
    TaskInstructionsGenerationTaskInput,
    TaskInstructionsGenerationTaskOutput,
)
from api.tasks.task_instruction_required_tools_picking.task_instructions_required_tools_picking_task import (
    TaskInstructionsRequiredToolsPickingTaskOutput,
)
from api.tasks.task_instructions_migration.task_instructions_migration_task import (
    TaskInstructionsMigrationTaskInput,
    TaskInstructionsMigrationTaskOutput,
)
from core.domain.deprecated.task import Task
from core.domain.errors import UnparsableChunkError
from core.domain.fields.chat_message import ChatMessage, UserChatMessage
from core.domain.fields.file import File
from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_image import TaskImage
from core.domain.task_info import TaskInfo
from core.domain.task_io import SerializableTaskIO
from core.domain.task_variant import SerializableTaskVariant
from core.domain.version_reference import VersionReference
from core.storage.mongo.models.task_group import TaskGroupDocument
from core.tasks.audio_transcription.audio_transcription_task import (
    AudioTranscriptionTask,
    AudioTranscriptionTaskInput,
    AudioTranscriptionTaskOutput,
)
from core.tasks.reformat_instructions.reformat_instructions_task import (
    TaskInstructionsReformatingTaskInput,
    TaskInstructionsReformatingTaskOutput,
)
from core.tasks.task_input_example.task_input_example_task import (
    TaskInputExampleTaskInput,
    TaskInputExampleTaskOutput,
)
from core.tasks.task_input_example.task_input_migration_task import (
    TaskInputMigrationTaskInput,
    TaskInputMigrationTaskOutput,
)
from core.tools import ToolKind
from tests.utils import mock_aiter


@pytest.fixture(scope="function")
def internal_tasks_service(mock_storage: Mock, mock_wai: Mock, mock_event_router: Mock):
    return InternalTasksService(wai=mock_wai, storage=mock_storage, event_router=mock_event_router)


@pytest.fixture
def task_variant() -> SerializableTaskVariant:
    return SerializableTaskVariant(
        id="test_variant_id",
        task_id="task_id",
        task_schema_id=1,
        name="TestTaskVariant",
        input_schema=SerializableTaskIO(
            version="1",
            json_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                },
                "required": ["key"],
            },
        ),
        output_schema=SerializableTaskIO(
            version="1",
            json_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                },
                "required": ["result"],
            },
        ),
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture(scope="function")
def mock_agent_summaries(mock_storage: Mock):
    with patch(
        "api.services.internal_tasks.internal_tasks_service.list_agent_summaries",
        return_value=[
            AgentSummary(
                name="test_agent_name",
                description="test_agent_description",
            ),
        ],
    ):
        yield


def agent_context() -> AgentBuilderInput.UserContent:
    return AgentBuilderInput.UserContent(
        company_name="test.com",
        company_description="test description",
        company_locations=["location1", "location2"],
        company_industries=["industry1", "industry2"],
        company_products=[
            Product(name="product1", features=None, description="product1 description", target_users=None),
            Product(name="product2", features=None, description="product2 description", target_users=None),
        ],
        current_agents=["test_agent_name: test_agent_description"],
    )


@pytest.fixture
def patched_internal_tools_description():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.internal_tools_description",
        return_value="hello",
        autospec=True,
    ) as mock:
        yield mock


@pytest.fixture
def mock_safe_generate_company_description():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.safe_generate_company_description_from_email",
        return_value=ExtractCompanyInfoFromDomainTaskOutput(
            company_name="test.com",
            description="test description",
            locations=["location1", "location2"],
            industries=["industry1", "industry2"],
            products=[
                Product(name="product1", description="product1 description"),
                Product(name="product2", description="product2 description"),
            ],
        ),
    ) as mock:
        yield mock


@pytest.fixture
def mock_format_instructions():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.format_instructions",
        new_callable=AsyncMock,
        return_value=TaskInstructionsReformatingTaskOutput(reformated_task_instructions="mock reformated instructions"),
    ) as mock:
        yield mock


class TestNewTask:
    async def test_new_task_new_schema(
        self,
        internal_tasks_service: InternalTasksService,
        mock_agent_summaries: Mock,
        mock_safe_generate_company_description: Mock,
        mock_agent_builder: Mock,
        patched_internal_tools_description: Mock,
    ):
        # Test the case when a new schema is actually generated + an assistant answer

        mock_output = AgentBuilderOutput(
            answer_to_user="mock assistant_answer",
            new_agent_schema=AgentSchema(
                agent_name="mock name",
                input_schema=InputObjectFieldConfig(
                    name="mock input_schema",
                    fields=[
                        InputGenericFieldConfig(
                            name="input string field",
                            type=InputSchemaFieldType.STRING,
                        ),
                    ],
                ),
                output_schema=OutputObjectFieldConfig(
                    name="mock output_schema",
                    fields=[OutputStringFieldConfig(name="output string field")],
                ),
            ),
        )

        mock_agent_builder.return_value = mock_output

        new_task_schema, assistant_answer = await internal_tasks_service.run_task_schema_iterations(
            chat_messages=[UserChatMessage(content="mock user message")],
            existing_task=None,
            user_email="john.doe@example.com",
        )

        # Asserts for input values
        assert mock_agent_builder.await_count == 1
        assert mock_agent_builder.call_args.args[0] == AgentBuilderInput(
            previous_messages=[],
            new_message=UserChatMessage(content="mock user message"),
            existing_agent_schema=None,
            user_context=agent_context(),
            available_tools_description="hello",
        )

        # Assert for the return values
        assert assistant_answer == "mock assistant_answer"
        assert new_task_schema
        assert new_task_schema.agent_name == "MockName"
        assert new_task_schema.input_json_schema == {
            "properties": {"input string field": {"type": "string"}},
            "type": "object",
        }
        assert new_task_schema.output_json_schema == {
            "properties": {"output string field": {"type": "string"}},
            "type": "object",
        }
        patched_internal_tools_description.assert_called_once_with(all=True)

    async def test_new_task_no_new_schema(
        self,
        internal_tasks_service: InternalTasksService,
        mock_agent_summaries: Mock,
        mock_storage: Mock,
        patched_internal_tools_description: Mock,
        mock_safe_generate_company_description: Mock,
        mock_agent_builder: Mock,
    ):
        # Test the case when NO new schema is actually generated,  an assistant answer ONLY

        mock_agent_builder.return_value = AgentBuilderOutput(
            answer_to_user="mock assistant_answer",
            new_agent_schema=None,
        )

        new_task_schema, assistant_answer = await internal_tasks_service.run_task_schema_iterations(
            chat_messages=[UserChatMessage(content="mock user message")],
            existing_task=None,
            user_email="john.doe@example.com",
        )

        # Asserts for input values
        assert mock_agent_builder.await_count == 1
        assert mock_agent_builder.call_args.args[0] == AgentBuilderInput(
            previous_messages=[],
            new_message=UserChatMessage(content="mock user message"),
            existing_agent_schema=None,
            user_context=agent_context(),
            available_tools_description="hello",
        )

        # Assert for the return values
        assert assistant_answer == "mock assistant_answer"
        assert not new_task_schema
        patched_internal_tools_description.assert_called_once_with(all=True)

    async def test_new_task_no_assistant_answer_no_schema(
        self,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        mock_agent_summaries: Mock,
        patched_internal_tools_description: Mock,
        mock_safe_generate_company_description: Mock,
        mock_agent_builder: Mock,
    ):
        # Test the case when NO assistant answer nor schema is returned by the 'ChatTaskSchemaGenerationTask' task.
        # Test that we correctly fallback back to the default answer

        mock_agent_builder.return_value = AgentBuilderOutput(
            answer_to_user="",
            new_agent_schema=None,
        )

        new_task_schema, assistant_answer = await internal_tasks_service.run_task_schema_iterations(
            chat_messages=[UserChatMessage(content="mock user message")],
            existing_task=None,
            user_email="john.doe@example.com",
        )

        # Asserts for input values
        assert mock_agent_builder.await_count == 1
        assert mock_agent_builder.call_args.args[0] == AgentBuilderInput(
            previous_messages=[],
            new_message=UserChatMessage(content="mock user message"),
            existing_agent_schema=None,
            user_context=agent_context(),
            available_tools_description="hello",
        )

        # Assert for the return values
        assert assistant_answer == "I did not understand your request. Can you try again ?"
        assert not new_task_schema
        patched_internal_tools_description.assert_called_once_with(all=True)

    async def test_new_task_no_assistant_answer_with_schema(
        self,
        internal_tasks_service: InternalTasksService,
        mock_agent_summaries: Mock,
        patched_internal_tools_description: Mock,
        mock_safe_generate_company_description: Mock,
        mock_agent_builder: Mock,
    ):
        # Test the case when NO assistant answer but a schema is returned by the 'ChatTaskSchemaGenerationTask' task.
        # Test that we correctly fallback back to the default answer

        mock_agent_builder.return_value = AgentBuilderOutput(
            answer_to_user="",
            new_agent_schema=AgentSchema(
                agent_name="mock name",
                input_schema=InputObjectFieldConfig(
                    name="mock input_schema",
                    fields=[
                        InputGenericFieldConfig(
                            name="input string field",
                            type=InputSchemaFieldType.STRING,
                        ),
                    ],
                ),
                output_schema=OutputObjectFieldConfig(
                    name="mock output_schema",
                    fields=[OutputStringFieldConfig(name="output string field")],
                ),
            ),
        )

        new_task_schema, assistant_answer = await internal_tasks_service.run_task_schema_iterations(
            chat_messages=[UserChatMessage(content="mock user message")],
            existing_task=None,
            user_email="john.doe@example.com",
        )

        # Asserts for input values
        assert mock_agent_builder.await_count == 1
        assert mock_agent_builder.call_args.args[0] == AgentBuilderInput(
            previous_messages=[],
            new_message=UserChatMessage(content="mock user message"),
            existing_agent_schema=None,
            user_context=agent_context(),
            available_tools_description="hello",
        )

        # Assert for the return values
        assert assistant_answer == "Here is the schema for task."
        assert new_task_schema
        assert new_task_schema.agent_name == "MockName"
        assert new_task_schema.input_json_schema == {
            "properties": {"input string field": {"type": "string"}},
            "type": "object",
        }
        assert new_task_schema.output_json_schema == {
            "properties": {"output string field": {"type": "string"}},
            "type": "object",
        }
        patched_internal_tools_description.assert_called_once_with(all=True)

    async def test_generate_task_instructions(
        self,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        patched_internal_tools_description: Mock,
    ):
        # Test for the 'generate_task_instructions' method
        with patch(
            "api.services.internal_tasks.internal_tasks_service.generate_task_instructions",
            new_callable=AsyncMock,
            return_value=TaskInstructionsGenerationTaskOutput(
                task_instructions="mock generated instructions",
            ),
        ) as mock_generate_task_instructions:
            task_instructions = await internal_tasks_service.generate_task_instructions(
                task_id="test_task",
                task_schema_id=1,
                chat_messages=[UserChatMessage(content="mock user message")],
                task=AgentSchemaJson(
                    agent_name="mock name",
                    input_json_schema={"schema": "mock input_schema"},
                    output_json_schema={"schema": "mock output_schema"},
                ),
                required_tool_kinds={ToolKind.WEB_SEARCH_GOOGLE},
            )

            # Assert for the return values
            assert task_instructions == "mock reformated instructions"

            # Verify task instructions generation call
            mock_generate_task_instructions.assert_awaited_once_with(
                TaskInstructionsGenerationTaskInput(
                    chat_messages=[UserChatMessage(content="mock user message")],
                    task=TaskInstructionsGenerationTaskInput.Task(
                        name="mock name",
                        input_json_schema={"schema": "mock input_schema"},
                        output_json_schema={"schema": "mock output_schema"},
                    ),
                    available_tools_description="hello",
                ),
            )

            # Verify reformatting call
            mock_format_instructions.assert_awaited_once_with(
                TaskInstructionsReformatingTaskInput(inital_task_instructions="mock generated instructions"),
            )
            patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})


class TestStreamTaskDescription:
    async def test_stream_task_description_generate(
        self,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
    ):
        task_id = "test_task_id"
        task_schema_id = 1
        generated_description = "This is a generated description."

        mock_storage.tasks.get_task_info = AsyncMock(
            return_value=TaskInfo(task_id=task_id, name="Test Task", is_public=True, description=None),
        )

        mock_task_variant = SerializableTaskVariant(
            id="test_id",
            task_id=task_id,
            task_schema_id=task_schema_id,
            name="Test Task",
            description=None,
            input_schema=SerializableTaskIO(version="1", json_schema={"foo": "bar"}),
            output_schema=SerializableTaskIO(version="1", json_schema={"foo1": "bar1"}),
        )

        mock_storage.task_variant_latest_by_schema_id.return_value = mock_task_variant

        with patch(
            "api.services.internal_tasks.internal_tasks_service.stream_task_description_generation",
            return_value=mock_aiter(
                TaskDescriptionGenerationTaskOutput(task_description="This is"),
                TaskDescriptionGenerationTaskOutput(task_description="This is a generated"),
                TaskDescriptionGenerationTaskOutput(task_description=generated_description),
            ),
        ) as mock_stream_task_description_generation:
            result = [
                chunk
                async for chunk in internal_tasks_service.set_task_description_if_missing(
                    task_id,
                    task_schema_id,
                    instructions="",
                )
            ]

            mock_stream_task_description_generation.assert_called_once_with(
                TaskDescriptionGenerationTaskInput(
                    chat_messages=[],
                    task_schema=AgentSchemaJson(
                        agent_name="Test Task",
                        input_json_schema={"foo": "bar"},
                        output_json_schema={"foo1": "bar1"},
                    ),
                    task_instructions="",
                ),
            )
            assert result == ["This is", "This is a generated", generated_description]
            mock_storage.tasks.get_task_info.assert_called_once_with(task_id)
            mock_storage.task_variant_latest_by_schema_id.assert_called_once_with(task_id, task_schema_id)
            mock_storage.set_task_description.assert_called_once_with(task_id, generated_description)

    async def test_stream_task_description_generate_already_exists(
        self,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
    ):
        task_id = "test_task_id"
        task_schema_id = 1
        existing_description = "This is an existing description."

        mock_storage.tasks.get_task_info = AsyncMock(
            return_value=TaskInfo(task_id=task_id, name="Test Task", is_public=True, description=existing_description),
        )

        mock_task_variant = SerializableTaskVariant(
            id="test_id",
            task_id=task_id,
            task_schema_id=task_schema_id,
            name="Test Task",
            description=None,
            input_schema=SerializableTaskIO(version="1", json_schema={"foo": "bar"}),
            output_schema=SerializableTaskIO(version="1", json_schema={"foo1": "bar1"}),
        )

        mock_storage.task_variant_latest_by_schema_id.return_value = mock_task_variant

        result = [
            chunk
            async for chunk in internal_tasks_service.set_task_description_if_missing(
                task_id,
                task_schema_id,
                instructions="",
            )
        ]

        assert result == [existing_description]
        mock_storage.tasks.get_task_info.assert_called_once_with(task_id)
        mock_storage.task_variant_latest_by_schema_id.assert_not_called()
        mock_storage.set_task_description.assert_not_awaited()


class TestGetTaskImage:
    async def test_get_existing_task_image(self, mock_storage: Mock, internal_tasks_service: InternalTasksService):
        task_id = "existing_task"
        existing_image = TaskImage(
            task_id=task_id,
            image_data=b"existing_image_data",
            compressed_image_data=b"compressed_existing_image_data",
        )

        mock_storage.get_task = AsyncMock()
        mock_storage.get_task_image = AsyncMock(return_value=existing_image)
        internal_tasks_service._generate_task_image = AsyncMock()  # type: ignore

        result = await internal_tasks_service.get_task_image(task_id)

        mock_storage.get_task.assert_called_once_with(task_id)
        mock_storage.get_task_image.assert_called_once_with(task_id)
        internal_tasks_service._generate_task_image.assert_not_called()  # type: ignore
        assert result == existing_image

    async def test_create_task_image_no_existing_image(
        self,
        mock_storage: Mock,
        internal_tasks_service: InternalTasksService,
    ):
        task_id = "test_task_id"
        task_name = "test_task_name"
        new_image_data = b"test_new_image_data"
        task_description = "test_task_description"

        mock_storage.tasks.get_task_info = AsyncMock(
            return_value=TaskInfo(task_id=task_id, name=task_name, is_public=True, description=task_description),
        )

        mock_storage.task_variant_latest_by_schema_id = AsyncMock()
        mock_storage.get_task_image = AsyncMock(return_value=None)
        mock_storage.create_task_image = AsyncMock()

        internal_tasks_service._generate_task_image = AsyncMock(return_value=new_image_data)  # type: ignore

        result = await internal_tasks_service.create_task_image(task_id=task_id)

        mock_storage.tasks.get_task_info.assert_called_once_with(task_id)
        mock_storage.task_variant_latest_by_schema_id.assert_not_called()
        mock_storage.get_task_image.assert_called_once_with(task_id)
        internal_tasks_service._generate_task_image.assert_called_once_with(task_description=task_description)  # type: ignore
        mock_storage.create_task_image.assert_called_once()

        assert isinstance(result, TaskImage)
        assert result.task_id == task_id
        assert result.image_data == new_image_data

    async def test_create_task_image_existing_image(
        self,
        mock_storage: Mock,
        internal_tasks_service: InternalTasksService,
    ):
        task_id = "test_task_id"
        new_image_data = b"test_new_image_data"

        mock_storage.tasks.get_task_info = AsyncMock()

        mock_storage.task_variant_latest_by_schema_id = AsyncMock()
        existing_image = TaskImage(
            task_id=task_id,
            image_data=b"existing_image_data",
            compressed_image_data=b"existing_compressed_image_data",
        )
        mock_storage.get_task_image = AsyncMock(return_value=existing_image)
        mock_storage.create_task_image = AsyncMock()

        internal_tasks_service._generate_task_image = AsyncMock(return_value=new_image_data)  # type: ignore

        result = await internal_tasks_service.create_task_image(task_id=task_id)

        mock_storage.tasks.get_task_info.assert_not_awaited()
        mock_storage.task_variant_latest_by_schema_id.assert_not_called()
        mock_storage.get_task_image.assert_called_once_with(task_id)
        internal_tasks_service._generate_task_image.assert_not_awaited()  # type: ignore
        mock_storage.create_task_image.assert_not_awaited()

        assert isinstance(result, TaskImage)
        assert result.task_id == task_id
        assert result == existing_image

    async def test_get_task_image_nonexistent_task(
        self,
        mock_storage: Mock,
        internal_tasks_service: InternalTasksService,
    ):
        task_id = "nonexistent_task"

        mock_storage.get_task = AsyncMock(side_effect=Exception("Task not found"))
        internal_tasks_service._generate_task_image = AsyncMock()  # type: ignore

        with pytest.raises(Exception, match="Task not found"):
            await internal_tasks_service.get_task_image(task_id)

        mock_storage.get_task.assert_called_once_with(task_id)
        mock_storage.get_task_image.assert_not_called()
        internal_tasks_service._generate_task_image.assert_not_called()  # type: ignore
        mock_storage.create_task_image.assert_not_called()


@pytest.fixture(scope="function")
def mock_stream_task_input_migration_task():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.stream_task_input_migration_task",
    ) as mock_stream_task_input_migration_task:
        yield mock_stream_task_input_migration_task


@pytest.fixture(scope="function")
def mock_run_input_generation_instructions():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.run_input_generation_instructions",
        new_callable=AsyncMock,
    ) as mock_run_input_generation_instructions:
        mock_run_input_generation_instructions.return_value = InputGenerationInstructionsOutput(
            input_generation_instructions="This is an example input generation instruction",
        )
        yield mock_run_input_generation_instructions


@pytest.fixture(scope="function")
def mock_run_task_input_example_task() -> Generator[Mock, None, None]:
    with patch(
        "api.services.internal_tasks.internal_tasks_service.run_task_input_example_task",
        new_callable=AsyncMock,
    ) as mock_run_task_input_example_task:
        mock_run_task_input_example_task.return_value = TaskInputExampleTaskOutput(
            task_input={"name": "4"},
        )
        yield mock_run_task_input_example_task


class TestGenerateTaskInputs:
    @classmethod
    def _input_gen_task(cls) -> Task[TaskInputExampleTaskInput, TaskInputExampleTaskOutput]:
        return Task(
            name="input_gen_task",
            schema_id=1,
            input_class=TaskInputExampleTaskInput,
            output_class=TaskInputExampleTaskOutput,
        )

    @pytest.fixture
    def _api_task(self):
        return SerializableTaskVariant(
            id="",
            name="",
            task_id="task_id",
            task_schema_id=1,
            input_schema=SerializableTaskIO(
                version="",
                json_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "int": {"type": "integer"},
                    },
                    "required": ["name"],
                },
            ),
            output_schema=SerializableTaskIO.from_json_schema(
                {
                    "properties": {
                        "say_hello": {"type": "string"},
                    },
                },
            ),
        )

    @pytest.fixture(scope="function")
    def mock_datetime(self, internal_tasks_service: InternalTasksService) -> Generator[Mock, None, None]:
        with patch("api.services.internal_tasks.internal_tasks_service.datetime", autospec=True) as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2024, month=1, day=1, hour=1, minute=1, second=1)
            yield mock_datetime

    @pytest.fixture(scope="function")
    def mock_run_task_input_migration_task(self):
        with patch(
            "api.services.internal_tasks.internal_tasks_service.run_task_input_migration_task",
            new_callable=AsyncMock,
        ) as mock_run_task_input_migration_task:
            mock_run_task_input_migration_task.return_value = TaskInputMigrationTaskOutput(
                migrated_task_input={"name": "migrated_name", "int": 42},
            )

            yield mock_run_task_input_migration_task

    @pytest.fixture(scope="function")
    def mock_stream_task_input_migration_task(self):
        with patch(
            "api.services.internal_tasks.internal_tasks_service.stream_task_input_migration_task",
        ) as mock_stream_task_input_migration_task:
            yield mock_stream_task_input_migration_task

    @pytest.fixture(scope="function")
    def mock_stream_task_input_example_task(self):
        with patch(
            "api.services.internal_tasks.internal_tasks_service.stream_task_input_example_task",
        ) as mock_stream_task_input_example_task:
            yield mock_stream_task_input_example_task

    async def test_not_stream(
        self,
        mock_datetime: Mock,
        mock_run_input_generation_instructions: Mock,
        mock_run_task_input_example_task: Mock,
        mock_stream_task_input_migration_task: Mock,
        internal_tasks_service: InternalTasksService,
        _api_task: SerializableTaskVariant,
    ):
        mock_stream_task_input_migration_task.return_value = mock_aiter(
            TaskInputMigrationTaskOutput(migrated_task_input={"name": "4"}),
        )

        result = await internal_tasks_service.get_task_input(
            task=_api_task,
            input_instructions="",
            base_input=None,
            stream=False,
        )
        assert result == {"name": "4"}

        mock_run_task_input_example_task.assert_awaited_once()

    async def test_stream_single(
        self,
        mock_datetime: Mock,
        mock_stream_task_input_example_task: Mock,
        mock_run_input_generation_instructions: AsyncMock,
        internal_tasks_service: InternalTasksService,
        _api_task: SerializableTaskVariant,
        mock_storage: Mock,
    ):
        mock_storage.task_runs.fetch_task_run_resources.return_value = mock_aiter()

        mock_stream_task_input_example_task.return_value = mock_aiter(
            TaskInputExampleTaskOutput(task_input={"name": "4"}),
            TaskInputExampleTaskOutput(task_input={"name": "413", "int": 1}),
            TaskInputExampleTaskOutput(task_input={"name": "413", "int": 12}),
        )

        iter = await internal_tasks_service.get_task_input(
            task=_api_task,
            input_instructions="",
            base_input=None,
            stream=True,
        )
        result = [chunk async for chunk in iter]
        assert result == [
            {"name": "4"},
            {"name": "413", "int": 1},
            {"name": "413", "int": 12},
        ]

    async def test_build_input_gen_task_input_label_stability(
        self,
        internal_tasks_service: InternalTasksService,
        _api_task: SerializableTaskVariant,
    ):
        # First call
        first_input = TaskInputExampleTaskInput(
            current_datetime=datetime.now(timezone.utc).isoformat(),
            task_name="test",
            input_json_schema={"name": "test"},
            output_json_schema={"name": "test"},
            additional_instructions="test instructions",
        )
        first_label = first_input.memory_id()

        # Wait 100ms
        await asyncio.sleep(0.1)

        # Second call with same parameters
        second_input = TaskInputExampleTaskInput(
            current_datetime=datetime.now(timezone.utc).isoformat(),
            task_name="test",
            input_json_schema={"name": "test"},
            output_json_schema={"name": "test"},
            additional_instructions="test instructions",
        )
        second_label = second_input.memory_id()

        # Labels should be identical despite time difference
        assert first_label == second_label

    async def test_migrate_input_not_stream(
        self,
        mock_run_task_input_migration_task: Mock,
        internal_tasks_service: InternalTasksService,
        _api_task: SerializableTaskVariant,
    ):
        # Test migrating input without streaming
        base_input = {"name": "old_name", "legacy_field": "value"}

        result = await internal_tasks_service.get_task_input(
            task=_api_task,
            input_instructions="",
            base_input=base_input,
            stream=False,
        )

        assert result == {"name": "migrated_name", "int": 42}

        # Verify the migration task was called with correct parameters
        mock_run_task_input_migration_task.assert_called_once()
        task_input = mock_run_task_input_migration_task.call_args[0][0]
        assert isinstance(task_input, TaskInputMigrationTaskInput)
        assert task_input.base_input == base_input
        assert task_input.task_name == _api_task.name
        assert task_input.input_json_schema == _api_task.input_schema.json_schema
        assert task_input.output_json_schema == _api_task.output_schema.json_schema

    async def test_migrate_input_stream(
        self,
        mock_datetime: Mock,
        internal_tasks_service: InternalTasksService,
        _api_task: SerializableTaskVariant,
    ):
        # Test migrating input with streaming
        base_input = {"name": "old_name", "legacy_field": "value"}

        with patch(
            "api.services.internal_tasks.internal_tasks_service.stream_task_input_migration_task",
        ) as mock_stream:
            mock_stream.return_value = mock_aiter(
                TaskInputMigrationTaskOutput(migrated_task_input={"name": "migrated_1"}),
                TaskInputMigrationTaskOutput(migrated_task_input={"name": "migrated_2", "int": 1}),
                TaskInputMigrationTaskOutput(migrated_task_input={"name": "migrated_final", "int": 42}),
            )

            iter = await internal_tasks_service.get_task_input(
                task=_api_task,
                input_instructions="",
                base_input=base_input,
                stream=True,
            )

            result = [chunk async for chunk in iter]
            assert result == [
                {"name": "migrated_1"},
                {"name": "migrated_2", "int": 1},
                {"name": "migrated_final", "int": 42},
            ]

            # Verify the migration task was called with correct parameters
            mock_stream.assert_called_once()
            task_input = mock_stream.call_args[0][0]
            assert isinstance(task_input, TaskInputMigrationTaskInput)
            assert task_input.base_input == base_input
            assert task_input.task_name == _api_task.name
            assert task_input.input_json_schema == _api_task.input_schema.json_schema
            assert task_input.output_json_schema == _api_task.output_schema.json_schema


class TestTranscribeAudio:
    async def test_transcribe_audio(
        self,
        internal_tasks_service: InternalTasksService,
        mock_wai: Mock,
    ):
        # Arrange
        mock_audio_file = File(
            content_type="audio/mp3",
            data="This is sample file content",
        )
        expected_transcription = "This is a transcription of the audio file."

        mock_wai.run = AsyncMock(
            return_value=AudioTranscriptionTaskOutput(transcription=expected_transcription),
        )

        # Act
        result = await internal_tasks_service.transcribe_audio(mock_audio_file, model=AUDIO_TRANSCRIPTION_MODEL.value)

        # Assert
        assert result == expected_transcription

        mock_wai.run.assert_called_once()
        call_args = mock_wai.run.call_args

        assert isinstance(call_args[0][0], AudioTranscriptionTask)
        assert isinstance(call_args[1]["input"], AudioTranscriptionTaskInput)
        assert call_args[1]["input"].audio_file == mock_audio_file
        assert isinstance(call_args[1]["group"], VersionReference)
        assert call_args[1]["group"].properties.model == AUDIO_TRANSCRIPTION_MODEL.value


@pytest.fixture
def mock_stream_task_instructions_generation():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.stream_task_instructions_generation",
        return_value=mock_aiter(
            TaskInstructionsGenerationTaskOutput(
                task_instructions="Initial instructions chunk.",
            ),
        ),
    ) as mock_stream_task_instructions_generation:
        yield mock_stream_task_instructions_generation


class TestInternalTasksService:
    async def test_stream_task_instructions(
        self,
        mock_stream_task_instructions_generation: Mock,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        patched_internal_tools_description: Mock,
    ):
        mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
            reformated_task_instructions="Reformatted instructions.",
        )

        # Act
        instructions = [
            chunk
            async for chunk in internal_tasks_service.stream_task_instructions(
                task_id="test_task",
                task_schema_id=1,
                chat_messages=[UserChatMessage(content="User message")],
                task=AgentSchemaJson(
                    agent_name="TestTask",
                    input_json_schema={"schema": "input_schema"},
                    output_json_schema={"schema": "output_schema"},
                ),
                required_tool_kinds={ToolKind.WEB_SEARCH_GOOGLE},
            )
        ]

        # Assert
        assert instructions == [
            "Initial instructions chunk.",
            "Reformatted instructions.",
        ]

        # Verify task instructions generation call
        mock_stream_task_instructions_generation.assert_called_once_with(
            TaskInstructionsGenerationTaskInput(
                chat_messages=[UserChatMessage(content="User message")],
                task=TaskInstructionsGenerationTaskInput.Task(
                    name="TestTask",
                    input_json_schema={"schema": "input_schema"},
                    output_json_schema={"schema": "output_schema"},
                ),
                available_tools_description="hello",
            ),
        )

        # Verify reformatting call
        mock_format_instructions.assert_awaited_once_with(
            TaskInstructionsReformatingTaskInput(
                inital_task_instructions="Initial instructions chunk.",
            ),
        )
        patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})


@pytest.fixture
def mock_run_task_instructions_required_tools_picking():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.run_task_instructions_required_tools_picking",
        new_callable=AsyncMock,
        return_value=TaskInstructionsRequiredToolsPickingTaskOutput(required_tools=["@search-google"]),
    ) as mock_run_task_instructions_required_tools_picking:
        yield mock_run_task_instructions_required_tools_picking


@pytest.fixture
def mock_stream_task_instructions_update():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.stream_task_instructions_update",
        return_value=mock_aiter(
            TaskInstructionsMigrationTaskOutput(
                new_task_instructions="Updated instructions",
            ),
        ),
    ) as mock_stream_task_instructions_update:
        yield mock_stream_task_instructions_update


class TestStreamSuggestedInstructions:
    @classmethod
    def _serializable_task_variant(cls, task_id: str, task_schema_id: int) -> SerializableTaskVariant:
        return SerializableTaskVariant(
            id=f"{task_id}_variant_{task_schema_id}",
            task_id=task_id,
            task_schema_id=task_schema_id,
            name=f"TestTaskVariant{task_schema_id}",
            input_schema=SerializableTaskIO(
                version="1",
                json_schema={"type": "object", "properties": {"input": {"type": "string"}}},
            ),
            output_schema=SerializableTaskIO(
                version="1",
                json_schema={"type": "object", "properties": {"output": {"type": "string"}}},
            ),
            created_at=datetime.now(timezone.utc),
        )

    async def test_stream_suggested_instructions_first_schema(
        self,
        mock_run_task_instructions_required_tools_picking: Mock,
        mock_stream_task_instructions_generation: Mock,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        patched_internal_tools_description: Mock,
    ):
        task_id = "test_task"
        task_schema_id = 1
        task_variant = self._serializable_task_variant(task_id, task_schema_id)
        chat_messages = [ChatMessage(role="USER", content="Migrate instructions")]

        mock_stream_task_instructions_generation.return_value = mock_aiter(
            TaskInstructionsGenerationTaskOutput(
                task_instructions="new instructions",
            ),
        )
        mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
            reformated_task_instructions="Reformatted new instructions",
        )
        expected_outputs = [
            "new instructions",
            "Reformatted new instructions",
        ]

        async for instruction in await internal_tasks_service.stream_suggested_instructions(
            task_variant,
            chat_messages,
        ):
            assert instruction in expected_outputs

        # Verify that we don't try to get previous instructions for first schema
        mock_storage.task_groups.get_latest_group_iteration.assert_not_called()
        mock_storage.task_variants.get_latest_task_variant.assert_not_called()

        # Verify task instructions generation call
        mock_stream_task_instructions_generation.assert_called_once_with(
            TaskInstructionsGenerationTaskInput(
                chat_messages=chat_messages,
                task=TaskInstructionsGenerationTaskInput.Task(
                    name=task_variant.name,
                    input_json_schema={"version": "1", "json_schema": task_variant.input_schema.json_schema},
                    output_json_schema={"version": "1", "json_schema": task_variant.output_schema.json_schema},
                ),
                available_tools_description="hello",
            ),
        )
        patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})

        # Verify reformatting call
        mock_format_instructions.assert_called_once_with(
            TaskInstructionsReformatingTaskInput(
                inital_task_instructions="new instructions",
            ),
        )

        # Verify required tools picking call
        mock_run_task_instructions_required_tools_picking.assert_awaited_once()

    async def test_stream_suggested_instructions_migrate_instructions(
        self,
        mock_run_task_instructions_required_tools_picking: Mock,
        mock_stream_task_instructions_generation: Mock,
        mock_format_instructions: Mock,
        mock_stream_task_instructions_update: Mock,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        patched_internal_tools_description: Mock,
    ):
        task_id = "test_task"
        task_schema_id = 2
        task_variant = self._serializable_task_variant(task_id, task_schema_id)
        former_task_variant = self._serializable_task_variant(task_id, task_schema_id - 1)
        chat_messages = [ChatMessage(role="USER", content="Migrate instructions")]

        # Mock behavior for migration
        mock_storage.task_groups.get_latest_group_iteration.side_effect = [
            None,  # No group with the same schema
            TaskGroup(
                iteration=1,
                properties=TaskGroupProperties(instructions="Old instructions"),
            ),
        ]
        mock_storage.task_variants.get_latest_task_variant = AsyncMock(
            return_value=self._serializable_task_variant(
                task_id,
                task_schema_id - 1,
            ),
        )

        mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
            reformated_task_instructions="Reformatted instructions",
        )

        expected_outputs = [
            "Updated instructions",
            "Reformatted instructions",
        ]

        async for instruction in await internal_tasks_service.stream_suggested_instructions(
            task_variant,
            chat_messages,
        ):
            assert instruction in expected_outputs

        # Verify task instructions migration call
        mock_stream_task_instructions_update.assert_called_once_with(
            TaskInstructionsMigrationTaskInput(
                initial_task_instructions="Old instructions",
                initial_task_schema=AgentSchemaJson(
                    agent_name=former_task_variant.name,
                    input_json_schema=former_task_variant.input_schema.json_schema,
                    output_json_schema=former_task_variant.output_schema.json_schema,
                ),
                chat_messages=chat_messages,
                new_task_schema=AgentSchemaJson(
                    agent_name=task_variant.name,
                    input_json_schema=task_variant.input_schema.json_schema,
                    output_json_schema=task_variant.output_schema.json_schema,
                ),
                available_tools_description="hello",
            ),
        )

        # Verify reformatting call
        mock_format_instructions.assert_called_once_with(
            TaskInstructionsReformatingTaskInput(
                inital_task_instructions="Updated instructions",
            ),
        )
        patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})

        # Verify required tools picking call
        mock_run_task_instructions_required_tools_picking.assert_awaited_once()

    async def test_stream_suggested_instructions_former_instructions_missing(
        self,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        patched_internal_tools_description: Mock,
    ):
        task_id = "test_task"
        task_schema_id = 2
        task_variant = self._serializable_task_variant(task_id, task_schema_id)
        chat_messages = [ChatMessage(role="USER", content="Migrate instructions")]

        # Mock behavior for migration
        mock_storage.task_groups.get_latest_group_iteration.side_effect = [
            None,  # No group with the same schema
            TaskGroup(
                iteration=1,
                properties=TaskGroupProperties(),  # No instructions
            ),
        ]
        mock_storage.task_variants.get_latest_task_variant = AsyncMock(
            return_value=self._serializable_task_variant(
                task_id,
                task_schema_id - 1,
            ),
        )

        # Mock the task instructions generation stream
        with (
            patch(
                "api.services.internal_tasks.internal_tasks_service.stream_task_instructions_generation",
                return_value=mock_aiter(
                    TaskInstructionsGenerationTaskOutput(
                        task_instructions="new instructions",
                    ),
                ),
            ) as mock_stream_task_instructions_generation,
            patch(
                "api.services.internal_tasks.internal_tasks_service.run_task_instructions_required_tools_picking",
                new_callable=AsyncMock,
                return_value=TaskInstructionsRequiredToolsPickingTaskOutput(required_tools=["@search-google"]),
            ) as mock_run_task_instructions_required_tools_picking,
        ):
            mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
                reformated_task_instructions="Reformatted new instructions",
            )

            expected_outputs = [
                "new instructions",
                "Reformatted new instructions",
            ]

            async for instruction in await internal_tasks_service.stream_suggested_instructions(
                task_variant,
                chat_messages,
            ):
                assert instruction in expected_outputs

            # Verify task instructions generation call
            mock_stream_task_instructions_generation.assert_called_once_with(
                TaskInstructionsGenerationTaskInput(
                    chat_messages=chat_messages,
                    task=TaskInstructionsGenerationTaskInput.Task(
                        name=task_variant.name,
                        input_json_schema={"version": "1", "json_schema": task_variant.input_schema.json_schema},
                        output_json_schema={"version": "1", "json_schema": task_variant.output_schema.json_schema},
                    ),
                    available_tools_description="hello",
                ),
            )

            # Verify reformatting call
            mock_format_instructions.assert_called_once_with(
                TaskInstructionsReformatingTaskInput(
                    inital_task_instructions="new instructions",
                ),
            )
            patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})

            # Verify required tools picking call
            mock_run_task_instructions_required_tools_picking.assert_awaited_once()

    async def test_stream_suggested_instructions_group_with_same_schema(
        self,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        patched_internal_tools_description: Mock,
    ):
        task_id = "test_task"
        task_schema_id = 2
        task_variant = self._serializable_task_variant(task_id, task_schema_id)
        chat_messages = [ChatMessage(role="USER", content="Migrate instructions")]

        # Mock behavior for migration
        mock_storage.task_groups.get_latest_group_iteration.side_effect = [
            TaskGroupDocument(
                iteration=1,
                properties={"instructions": "instructions for same schema"},
            ),
            TaskGroupDocument(
                iteration=2,
                properties={"instructions": "Old instructions"},
            ),
        ]
        mock_storage.task_variants.get_latest_task_variant = AsyncMock(
            return_value=self._serializable_task_variant(
                task_id,
                task_schema_id - 1,
            ),
        )

        # Mock the task instructions generation stream
        with (
            patch(
                "api.services.internal_tasks.internal_tasks_service.stream_task_instructions_generation",
                return_value=mock_aiter(
                    TaskInstructionsGenerationTaskOutput(
                        task_instructions="new instructions",
                    ),
                ),
            ) as mock_stream_task_instructions_generation,
            patch(
                "api.services.internal_tasks.internal_tasks_service.run_task_instructions_required_tools_picking",
                new_callable=AsyncMock,
                return_value=TaskInstructionsRequiredToolsPickingTaskOutput(required_tools=["@search-google"]),
            ) as mock_run_task_instructions_required_tools_picking,
        ):
            mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
                reformated_task_instructions="Reformatted new instructions",
            )

            expected_outputs = [
                "new instructions",
                "Reformatted new instructions",
            ]
            async for instruction in await internal_tasks_service.stream_suggested_instructions(
                task_variant,
                chat_messages,
            ):
                assert instruction in expected_outputs

            # Verify task instructions generation call
            mock_stream_task_instructions_generation.assert_called_once_with(
                TaskInstructionsGenerationTaskInput(
                    chat_messages=chat_messages,
                    task=TaskInstructionsGenerationTaskInput.Task(
                        name=task_variant.name,
                        input_json_schema={"version": "1", "json_schema": task_variant.input_schema.json_schema},
                        output_json_schema={"version": "1", "json_schema": task_variant.output_schema.json_schema},
                    ),
                    available_tools_description="hello",
                ),
            )

            # Verify reformatting call
            mock_format_instructions.assert_called_once_with(
                TaskInstructionsReformatingTaskInput(
                    inital_task_instructions="new instructions",
                ),
            )
            patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})

            # Verify required tools picking call
            mock_run_task_instructions_required_tools_picking.assert_awaited_once()


class TestInternalTasksServiceHelpers:
    def test_handle_stream_task_iterations_chunk_with_complete_schema(
        self,
        internal_tasks_service: InternalTasksService,
    ):
        # Arrange
        chunk = AgentBuilderOutput(
            answer_to_user="mock assistant_answer",
            new_agent_schema=AgentSchema(
                agent_name="mock name",
                input_schema=InputObjectFieldConfig(
                    name="mock input_schema",
                    fields=[InputGenericFieldConfig(name="input string field", type=InputSchemaFieldType.STRING)],
                ),
                output_schema=OutputObjectFieldConfig(
                    name="mock output_schema",
                    fields=[OutputStringFieldConfig(name="output string field")],
                ),
            ),
        )

        # Act
        new_task_schema, assistant_answer = internal_tasks_service._handle_stream_task_iterations_chunk(chunk)  # pyright: ignore[reportPrivateUsage]

        # Assert
        assert assistant_answer == "mock assistant_answer"
        assert new_task_schema
        assert new_task_schema.agent_name == "MockName"
        assert new_task_schema.input_json_schema == {
            "properties": {"input string field": {"type": "string"}},
            "type": "object",
        }
        assert new_task_schema.output_json_schema == {
            "properties": {"output string field": {"type": "string"}},
            "type": "object",
        }

    def test_handle_stream_task_iterations_chunk_with_partial_schema(
        self,
        internal_tasks_service: InternalTasksService,
    ):
        # Arrange
        chunk = AgentBuilderOutput(
            answer_to_user="mock assistant_answer",
            new_agent_schema=AgentSchema(
                agent_name="mock name",
                input_schema=InputObjectFieldConfig(
                    name="output",
                    fields=[
                        InputArrayFieldConfig(
                            name="meal_plan",
                            item_type=InputObjectFieldConfig(
                                name="daily_meals",
                                fields=[
                                    InputArrayFieldConfig(
                                        name="meals",
                                        item_type=InputObjectFieldConfig(
                                            name="meal",
                                            fields=[
                                                InputGenericFieldConfig(
                                                    name="name",
                                                    type=InputSchemaFieldType.STRING,
                                                    description="Name of the meal",
                                                ),
                                                EnumFieldConfig(
                                                    name="type",
                                                    values=["BREAKFAST", "LUNCH", "DINNER", "SNACK", "OTHER"],
                                                ),
                                                InputGenericFieldConfig(
                                                    name="description",
                                                    type=InputSchemaFieldType.STRING,
                                                    description="Brief description of the meal",
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        )

        new_task_schema, assistant_answer = internal_tasks_service._handle_stream_task_iterations_chunk(chunk)  # pyright: ignore[reportPrivateUsage]

        # Assert
        assert assistant_answer == "mock assistant_answer"
        assert new_task_schema
        assert new_task_schema.agent_name == "MockName"
        assert not new_task_schema.output_json_schema

    def test_handle_stream_task_iterations_chunk_with_no_schema(self, internal_tasks_service: InternalTasksService):
        # Arrange
        chunk = AgentBuilderOutput(
            answer_to_user="mock assistant_answer",
            new_agent_schema=None,  # No schema
        )

        # Act
        new_task_schema, assistant_answer = internal_tasks_service._handle_stream_task_iterations_chunk(chunk)  # pyright: ignore[reportPrivateUsage]

        # Assert
        assert assistant_answer == "mock assistant_answer"
        assert new_task_schema is None


@pytest.fixture(scope="function")
def mock_generate_changelog_from_properties():
    with patch(
        "api.services.internal_tasks.internal_tasks_service.generate_changelog_from_properties",
        new_callable=AsyncMock,
        return_value=GenerateChangelogFromPropertiesTaskOutput(changes=["This is a change", "This is another change"]),
    ) as mock:
        yield mock


class TestGenerateChangelog:
    async def test_with_schemas(
        self,
        mock_generate_changelog_from_properties: Mock,
        mock_storage: Mock,
        task_variant: SerializableTaskVariant,
        internal_tasks_service: InternalTasksService,
    ):
        async def task_version_resource_by_id(task_id: str, task_variant_id: str):
            if task_variant_id == "old":
                copied = task_variant.model_copy()
                copied.input_schema.json_schema["properties"] = {"hello": {"type": "string"}}
                return copied
            return task_variant

        mock_storage.task_version_resource_by_id.side_effect = task_version_resource_by_id

        item = await internal_tasks_service.generate_changelog(
            tenant="tenant",
            task_id="task_id",
            task_schema_id=1,
            major_from=1,
            major_to=2,
            old_task_group=TaskGroupProperties.model_validate({"task_variant_id": "old"}),
            new_task_group=TaskGroupProperties.model_validate({"task_variant_id": "new"}),
        )

        assert item
        assert item.changelog == [
            "This is a change",
            "This is another change",
        ]

        assert mock_generate_changelog_from_properties.call_args.args[0] == GenerateChangelogFromPropertiesTaskInput(
            old_task_group=TaskGroupWithSchema(
                properties=Properties(temperature=None, instructions=None, few_shot=False),
                schema=Schema(
                    input_json_schema='{"type": "object", "properties": {"hello": {"type": "string"}}, "required": ["key"]}',
                    output_json_schema='{"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}',
                ),
            ),
            new_task_group=TaskGroupWithSchema(
                properties=Properties(temperature=None, instructions=None, few_shot=False),
                schema=Schema(
                    input_json_schema='{"type": "object", "properties": {"hello": {"type": "string"}}, "required": ["key"]}',
                    output_json_schema='{"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}',
                ),
            ),
        )


@pytest.fixture(scope="function")
def mock_stream_agent_builder(monkeypatch: pytest.MonkeyPatch) -> Mock:
    from api.services.internal_tasks import internal_tasks_service

    mock_func = Mock()

    monkeypatch.setattr(internal_tasks_service, internal_tasks_service.agent_builder.__name__, mock_func)
    return mock_func


@pytest.fixture(scope="function")
def mock_agent_builder(monkeypatch: pytest.MonkeyPatch) -> Mock:
    from api.services.internal_tasks import internal_tasks_service

    mock_func = AsyncMock()

    monkeypatch.setattr(internal_tasks_service, internal_tasks_service.agent_builder.__name__, mock_func)
    return mock_func


class TestStreamTaskIterations:
    async def test_stream_task_iterations_supports_error(
        self,
        internal_tasks_service: InternalTasksService,
        mock_storage: Mock,
        mock_stream_agent_builder: Mock,
        mock_agent_summaries: Mock,
        mock_safe_generate_company_description: Mock,
    ):
        mock_stream_agent_builder.stream.return_value = mock_aiter(
            Mock(
                output=AgentBuilderOutput(
                    answer_to_user="mock assistant_answer",
                    new_agent_schema=None,
                ),
            ),
            Mock(
                output=AgentBuilderOutput(
                    answer_to_user="mock assistant_answer",
                    new_agent_schema=None,
                ),
            ),
        )

        internal_tasks_service._handle_stream_task_iterations_chunk = Mock(  # pyright: ignore[reportPrivateUsage]
            side_effect=[
                UnparsableChunkError("Test exception"),
                (
                    AgentSchemaJson(
                        agent_name="name",
                        input_json_schema={"type": "objet"},
                        output_json_schema={"type": "objet"},
                    ),
                    "assistant_answer",
                ),
            ],
        )

        results = [
            result
            async for result in internal_tasks_service.stream_task_schema_iterations(
                chat_messages=[ChatMessage(role="USER", content="Hello")],
                user_email="john.doe@example.com",
            )
        ]

        assert results == [
            # First chunk is skipped as it raises KeyError("Test exception")
            (
                AgentSchemaJson(
                    agent_name="name",
                    input_json_schema={"type": "objet"},
                    output_json_schema={"type": "objet"},
                ),
                "assistant_answer",
            ),
        ]

    async def test_update_task_instructions(
        self,
        mock_format_instructions: Mock,
        internal_tasks_service: InternalTasksService,
        patched_internal_tools_description: Mock,
    ):
        # Mock the task instructions update
        with patch(
            "api.services.internal_tasks.internal_tasks_service.update_task_instructions",
            new_callable=AsyncMock,
            return_value=TaskInstructionsMigrationTaskOutput(
                new_task_instructions="mock updated instructions",
            ),
        ) as mock_update_task_instructions:
            mock_format_instructions.return_value = TaskInstructionsReformatingTaskOutput(
                reformated_task_instructions="mock reformated instructions",
            )

            # Act
            result = await internal_tasks_service.update_task_instructions(
                initial_task_schema=AgentSchemaJson(agent_name="test"),
                initial_task_instructions="initial instructions",
                new_task_schema=AgentSchemaJson(agent_name="test"),
                chat_messages=[UserChatMessage(content="test")],
                required_tool_kinds={ToolKind.WEB_SEARCH_GOOGLE},
            )

            # Assert
            assert result == "mock reformated instructions"

            # Verify task instructions update call
            mock_update_task_instructions.assert_awaited_once_with(
                TaskInstructionsMigrationTaskInput(
                    initial_task_instructions="initial instructions",
                    initial_task_schema=AgentSchemaJson(agent_name="test"),
                    chat_messages=[UserChatMessage(content="test")],
                    new_task_schema=AgentSchemaJson(agent_name="test"),
                    available_tools_description="hello",
                ),
            )

            # Verify reformatting call
            mock_format_instructions.assert_awaited_once_with(
                TaskInstructionsReformatingTaskInput(
                    inital_task_instructions="mock updated instructions",
                ),
            )
            patched_internal_tools_description.assert_called_once_with(include={ToolKind.WEB_SEARCH_GOOGLE})
