from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.services.internal_tasks.agent_suggestions_service import (
    SuggestLlmAgentsForCompanyOutputAndStatus,
    TaskSuggestionsService,
)
from api.tasks.agent_input_output_example import SuggestedAgentInputOutputExampleOutput
from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import (
    AgentBuilderOutput,
    AgentSchema,
    InputObjectFieldConfig,
    OutputObjectFieldConfig,
)
from api.tasks.detect_company_domain_task import (
    DetectCompanyDomainTaskInput,
    DetectCompanyDomainTaskOutput,
)
from api.tasks.extract_company_info_from_domain_task import (
    ExtractCompanyInfoFromDomainTaskInput,
    ExtractCompanyInfoFromDomainTaskOutput,
    Product,
)
from api.tasks.suggest_llm_features_for_company_agent import (
    AgentSuggestionChatMessage,
    SuggestedAgent,
    SuggestLlmAgentForCompanyOutput,
)
from core.domain.fields.chat_message import ChatMessage
from core.storage.backend_storage import BackendStorage
from tests.utils import mock_aiter


@pytest.fixture
def service():
    return TaskSuggestionsService()


class TestTaskSuggestionsService:
    async def test_stream_task_suggestions_with_successful_domain_detection(self, service: TaskSuggestionsService):
        # Arrange
        messages = [AgentSuggestionChatMessage(role="USER", content_str="Hi, I work at test.com")]

        mock_domain_detection = DetectCompanyDomainTaskOutput(
            company_domain="test.com",
        )

        mock_company_info = ExtractCompanyInfoFromDomainTaskOutput(
            company_name="TestCo",
            description="A test company",
            locations=["USA"],
            industries=["Technology"],
            products=[
                Product(
                    name="Test Product",
                    features=["Feature 1", "Feature 2"],
                    description="A test product",
                    target_users=["Developers"],
                ),
            ],
        )

        mock_suggestions = [
            SuggestLlmAgentForCompanyOutput(
                assistant_message=AgentSuggestionChatMessage(role="ASSISTANT", content_str="Suggestion 1"),
            ),
            SuggestLlmAgentForCompanyOutput(
                assistant_message=AgentSuggestionChatMessage(role="ASSISTANT", content_str="Suggestion 2"),
            ),
        ]

        with (
            patch(
                "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
                new_callable=AsyncMock,
                return_value=mock_domain_detection,
            ) as mock_detect,
            patch(
                "api.tasks.extract_company_info_from_domain_task._extract_company_info_from_domain",
                new_callable=AsyncMock,
                return_value=mock_company_info,
            ) as mock_extract,
            patch(
                "api.services.internal_tasks.agent_suggestions_service.suggest_llm_agents_for_company",
                return_value=mock_aiter(*mock_suggestions),
            ) as mock_stream,
        ):
            mock_storage = Mock(spec=BackendStorage)
            mock_storage.fetch_tasks = Mock(return_value=mock_aiter())
            results = [c async for c in service.stream_agent_suggestions(messages, storage=mock_storage)]

            # Assert
            assert len(results) == 5  # 3 status updates + 2 suggestions
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="analyzing_company_context",
            )
            assert results[2] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
            )
            assert results[3] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="Suggestion 1",
                ),
            )

            mock_detect.assert_awaited_once_with(
                DetectCompanyDomainTaskInput(
                    messages=[ChatMessage(role="USER", content="Hi, I work at test.com")],
                ),
            )
            mock_extract.assert_awaited_once_with(
                ExtractCompanyInfoFromDomainTaskInput(company_domain="test.com"),
                use_cache="always",
            )
            mock_stream.assert_called_once()
            mock_storage.fetch_tasks.assert_called_once()
            call_args = mock_stream.call_args[0][0]
            assert call_args.messages == messages
            assert call_args.company_context.company_name == "TestCo"

    async def test_stream_task_suggestions_with_failed_domain_detection(self, service: TaskSuggestionsService):
        # Arrange
        messages = [AgentSuggestionChatMessage(role="USER", content_str="Hi, can you help me?")]

        mock_domain_detection = DetectCompanyDomainTaskOutput(
            company_domain=None,
            failure_assistant_answer="I couldn't detect your company domain. Could you please provide it?",
        )

        with patch(
            "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
            new_callable=AsyncMock,
            return_value=mock_domain_detection,
        ) as mock_detect:
            mock_storage = Mock(spec=BackendStorage)
            mock_storage.fetch_tasks = Mock(return_value=mock_aiter())
            results = [c async for c in service.stream_agent_suggestions(messages, storage=mock_storage)]

            # Assert
            assert len(results) == 2  # Initial status + failure message
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="I couldn't detect your company domain. Could you please provide it?",
                ),
            )

            mock_detect.assert_awaited_once_with(
                DetectCompanyDomainTaskInput(
                    messages=[ChatMessage(role="USER", content="Hi, can you help me?")],
                ),
            )
            mock_storage.fetch_tasks.assert_not_called()

    async def test_stream_task_suggestions_with_empty_messages(self, service: TaskSuggestionsService):
        # Test with empty messages list
        mock_domain_detection = DetectCompanyDomainTaskOutput(
            company_domain=None,
            failure_assistant_answer="Please provide your company domain to get started.",
        )

        with patch(
            "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
            new_callable=AsyncMock,
            return_value=mock_domain_detection,
        ) as mock_detect:
            mock_storage = Mock(spec=BackendStorage)
            mock_storage.fetch_tasks = Mock(return_value=mock_aiter())
            results = [c async for c in service.stream_agent_suggestions([], storage=mock_storage)]

            assert len(results) == 2
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="Please provide your company domain to get started.",
                ),
            )

            mock_detect.assert_awaited_once_with(DetectCompanyDomainTaskInput(messages=[]))
            mock_storage.fetch_tasks.assert_not_called()

    async def test_stream_task_suggestions_with_none_messages(self, service: TaskSuggestionsService):
        # Test with None messages
        mock_domain_detection = DetectCompanyDomainTaskOutput(
            company_domain=None,
            failure_assistant_answer="Please provide your company domain to get started.",
        )

        with patch(
            "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
            new_callable=AsyncMock,
            return_value=mock_domain_detection,
        ) as mock_detect:
            mock_storage = Mock(spec=BackendStorage)
            mock_storage.fetch_tasks = Mock(return_value=mock_aiter())
            results = [c async for c in service.stream_agent_suggestions(None, storage=mock_storage)]

            assert len(results) == 2
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="Please provide your company domain to get started.",
                ),
            )

            mock_detect.assert_awaited_once_with(DetectCompanyDomainTaskInput(messages=[]))
            mock_storage.fetch_tasks.assert_not_called()

    async def test_stream_task_output_preview_with_valid_task(self, service: TaskSuggestionsService):
        # Arrange
        suggested_task = SuggestedAgent(
            agent_description="Test task",
            explanation="Test explanation",
            input_specifications="input specs",
            output_specifications="output specs",
            department="Engineering",
        )

        mock_schema = AgentSchema(
            agent_name="Test Task",
            input_schema=InputObjectFieldConfig(),
            output_schema=OutputObjectFieldConfig(),
        )

        mock_schema_gen_output = AgentBuilderOutput(
            answer_to_user="Test answer",
            new_agent_schema=mock_schema,
        )

        mock_preview_chunks = [
            SuggestedAgentInputOutputExampleOutput(agent_output_example={"example": "Example"}),
            SuggestedAgentInputOutputExampleOutput(agent_output_example={"example": "Example string"}),
        ]

        with (
            patch(
                "api.services.internal_tasks.agent_suggestions_service.agent_builder",
                new_callable=AsyncMock,
                return_value=mock_schema_gen_output,
            ) as mock_run_schema,
            patch(
                "api.services.internal_tasks.agent_suggestions_service.stream_suggested_agent_input_output_example",
                return_value=mock_aiter(*mock_preview_chunks),
            ) as mock_stream,
        ):
            # Act
            results = [c async for c in service.stream_agent_output_preview(suggested_task)]

            # Assert
            assert len(results) == 2
            assert results[0].agent_output_example == {"example": "Example"}
            assert results[1].agent_output_example == {"example": "Example string"}

            mock_run_schema.assert_awaited_once()
            schema_input = mock_run_schema.call_args[0][0]
            assert schema_input.new_message.content == (
                "Test task\nTest explanation\nInput: input specs\nOutput: output specs\n"
            )

            mock_stream.assert_called_once()
            preview_input = mock_stream.call_args[0][0]
            assert preview_input.agent_description == "Test task"
            assert preview_input.explaination == "Test explanation"
            assert preview_input.destination_department == "Engineering"

    async def test_stream_task_output_preview_with_no_schema(self, service: TaskSuggestionsService):
        # Test when schema generation returns no schema
        suggested_task = SuggestedAgent(
            agent_description="Test task",
            explanation="Test explanation",
            input_specifications="input specs",
            output_specifications="output specs",
            department="Engineering",
        )

        mock_schema_gen_output = AgentBuilderOutput(
            answer_to_user="Test answer",
            new_agent_schema=None,  # No schema generated
        )

        with (
            patch(
                "api.services.internal_tasks.agent_suggestions_service.agent_builder",
                new_callable=AsyncMock,
                return_value=mock_schema_gen_output,
            ),
            patch(
                "api.services.internal_tasks.agent_suggestions_service.stream_suggested_agent_input_output_example",
                return_value=mock_aiter(
                    SuggestedAgentInputOutputExampleOutput(agent_output_example={"example": "Example"}),
                ),
            ) as mock_stream,
        ):
            results = [c async for c in service.stream_agent_output_preview(suggested_task)]

            assert len(results) == 1
            preview_input = mock_stream.call_args[0][0]
            assert preview_input.input_json_schema is None
            assert preview_input.output_json_schema is None

    async def test_stream_task_suggestions_with_provided_domain(self, service: TaskSuggestionsService):
        # Arrange
        messages = [AgentSuggestionChatMessage(role="USER", content_str="Hi, can you help me?")]
        user_email = "john@example.com"

        mock_company_info = ExtractCompanyInfoFromDomainTaskOutput(
            company_name="ExampleCo",
            description="An example company",
            locations=["USA"],
            industries=["Technology"],
            products=[
                Product(
                    name="Example Product",
                    features=["Feature 1"],
                    description="An example product",
                    target_users=["Users"],
                ),
            ],
        )

        mock_suggestions = [
            SuggestLlmAgentForCompanyOutput(
                assistant_message=AgentSuggestionChatMessage(role="ASSISTANT", content_str="Suggestion 1"),
            ),
        ]

        with (
            patch(
                "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
            ) as mock_detect,
            patch(
                "api.services.internal_tasks.agent_suggestions_service.safe_extract_company_domain",
                return_value=ExtractCompanyInfoFromDomainTaskInput(company_domain="example.com"),
            ),
            patch(
                "api.services.internal_tasks.agent_suggestions_service.safe_generate_company_description_from_domain",
                return_value=mock_company_info,
            ) as mock_extract,
            patch(
                "api.services.internal_tasks.agent_suggestions_service.suggest_llm_agents_for_company",
                return_value=mock_aiter(*mock_suggestions),
            ) as mock_stream,
        ):
            # Act
            mock_storage = Mock(spec=BackendStorage)
            mock_storage.fetch_tasks = Mock(return_value=mock_aiter())
            results = [
                c
                async for c in service.stream_agent_suggestions(
                    messages,
                    user_email=user_email,
                    storage=mock_storage,
                )
            ]

            # Assert
            assert len(results) == 3  # 2 status updates + 1 suggestion
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="analyzing_company_context",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
            )
            assert results[2] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="Suggestion 1",
                ),
            )

            # Verify domain detection was not called
            mock_detect.assert_not_called()

            # Verify company info extraction was called with provided domain
            mock_extract.assert_awaited_once_with(
                ExtractCompanyInfoFromDomainTaskInput(company_domain="example.com"),
            )

            # Verify task suggestions were generated with correct context
            assert mock_stream.call_count == 1
            call_args = mock_stream.call_args[0][0]
            assert call_args.messages == messages
            assert call_args.company_context.company_name == "ExampleCo"
            mock_storage.fetch_tasks.assert_called_once()

    async def test_stream_task_suggestions_with_successful_domain_detection_no_storage(
        self,
        service: TaskSuggestionsService,
    ):
        # Happy path without storage provider

        # Arrange
        messages = [AgentSuggestionChatMessage(role="USER", content_str="Hi, I work at test.com")]

        mock_domain_detection = DetectCompanyDomainTaskOutput(
            company_domain="test.com",
        )

        mock_company_info = ExtractCompanyInfoFromDomainTaskOutput(
            company_name="TestCo",
            description="A test company",
            locations=["USA"],
            industries=["Technology"],
            products=[
                Product(
                    name="Test Product",
                    features=["Feature 1", "Feature 2"],
                    description="A test product",
                    target_users=["Developers"],
                ),
            ],
        )

        mock_suggestions = [
            SuggestLlmAgentForCompanyOutput(
                assistant_message=AgentSuggestionChatMessage(role="ASSISTANT", content_str="Suggestion 1"),
            ),
            SuggestLlmAgentForCompanyOutput(
                assistant_message=AgentSuggestionChatMessage(role="ASSISTANT", content_str="Suggestion 2"),
            ),
        ]

        with (
            patch(
                "api.services.internal_tasks.agent_suggestions_service.run_detect_company_domain_task",
                new_callable=AsyncMock,
                return_value=mock_domain_detection,
            ) as mock_detect,
            patch(
                "api.tasks.extract_company_info_from_domain_task._extract_company_info_from_domain",
                new_callable=AsyncMock,
                return_value=mock_company_info,
            ) as mock_extract,
            patch(
                "api.services.internal_tasks.agent_suggestions_service.suggest_llm_agents_for_company",
                return_value=mock_aiter(*mock_suggestions),
            ) as mock_stream,
        ):
            results = [c async for c in service.stream_agent_suggestions(messages, storage=None)]

            # Assert
            assert len(results) == 5  # 3 status updates + 2 suggestions
            assert results[0] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )
            assert results[1] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="analyzing_company_context",
            )
            assert results[2] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
            )
            assert results[3] == SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
                assistant_message=AgentSuggestionChatMessage(
                    role="ASSISTANT",
                    content_str="Suggestion 1",
                ),
            )

            mock_detect.assert_awaited_once_with(
                DetectCompanyDomainTaskInput(
                    messages=[ChatMessage(role="USER", content="Hi, I work at test.com")],
                ),
            )
            mock_extract.assert_awaited_once_with(
                ExtractCompanyInfoFromDomainTaskInput(company_domain="test.com"),
                use_cache="always",
            )
            mock_stream.assert_called_once()
            call_args = mock_stream.call_args[0][0]
            assert call_args.messages == messages
            assert call_args.company_context.company_name == "TestCo"
