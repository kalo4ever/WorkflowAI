from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from api.services.internal_tasks.meta_agent_service import (
    MetaAgentService,
)
from api.tasks.extract_company_info_from_domain_task import Product
from api.tasks.meta_agent import MetaAgentInput, MetaAgentOutput
from core.domain.events import MetaAgentChatMessagesSent
from core.domain.fields.chat_message import ChatMessage
from core.storage.backend_storage import BackendStorage
from tests.utils import mock_aiter


class TestMetaAgentService:
    @pytest.mark.parametrize(
        "user_email, messages, company_description, current_agents, expected_input",
        [
            (
                "user@example.com",
                [ChatMessage(role="USER", content="Hello")],
                Mock(
                    company_name="Example Corp",
                    description="A tech company",
                    locations=["San Francisco"],
                    industries=["Technology"],
                    products=[Product(name="Product A", description="Description A")],
                ),
                ["Agent 1", "Agent 2"],
                MetaAgentInput(
                    messages=[ChatMessage(role="USER", content="Hello")],
                    company_context=MetaAgentInput.CompanyContext(
                        company_name="Example Corp",
                        company_description="A tech company",
                        company_locations=["San Francisco"],
                        company_industries=["Technology"],
                        company_products=[Product(name="Product A", description="Description A")],
                        current_agents=["Agent 1", "Agent 2"],
                    ),
                    workflowai_documentation="API Documentation",
                ),
            ),
            (
                None,  # No user email
                [ChatMessage(role="USER", content="Help")],
                None,  # No company description
                [],  # No agents
                MetaAgentInput(
                    messages=[ChatMessage(role="USER", content="Help")],
                    company_context=MetaAgentInput.CompanyContext(
                        company_name=None,
                        company_description=None,
                        company_locations=None,
                        company_industries=None,
                        company_products=None,
                        current_agents=[],
                    ),
                    workflowai_documentation="API Documentation",
                ),
            ),
        ],
    )
    async def test_build_meta_agent_input(
        self,
        user_email: str | None,
        messages: list[ChatMessage],
        company_description: Any,
        current_agents: list[str],
        expected_input: MetaAgentInput,
    ) -> None:
        # Create a mock storage
        mock_storage = Mock(spec=BackendStorage)
        mock_event_router = Mock()
        # Create the service with the mock storage
        service = MetaAgentService(storage=mock_storage, event_router=mock_event_router)

        # Mock the dependencies
        with (
            patch(
                "api.services.internal_tasks.meta_agent_service.safe_generate_company_description_from_email",
                new_callable=AsyncMock,
                return_value=company_description,
            ) as mock_generate_company_description,
            patch(
                "api.services.internal_tasks.meta_agent_service.list_agent_summaries",
                new_callable=AsyncMock,
                return_value=current_agents,
            ) as mock_list_agents,
            patch(
                "api.services.internal_tasks.meta_agent_service.build_api_docs_prompt",
                return_value="API Documentation",
            ) as mock_build_docs,
        ):
            # Call the method
            result = await service._build_meta_agent_input(user_email, messages)  # pyright: ignore[reportPrivateUsage]

            # Verify the mocks were called correctly
            mock_generate_company_description.assert_called_once_with(user_email)
            mock_list_agents.assert_called_once_with(mock_storage, limit=10)
            mock_build_docs.assert_called_once()

            # Verify the result
            assert result.messages == expected_input.messages
            assert result.company_context.company_name == expected_input.company_context.company_name
            assert result.company_context.company_description == expected_input.company_context.company_description
            assert result.company_context.company_locations == expected_input.company_context.company_locations
            assert result.company_context.company_industries == expected_input.company_context.company_industries
            assert result.company_context.current_agents == expected_input.company_context.current_agents
            assert result.workflowai_documentation == expected_input.workflowai_documentation

            # If company products exist, verify them
            if result.company_context.company_products and expected_input.company_context.company_products:
                for i, product in enumerate(result.company_context.company_products):
                    assert product.name == expected_input.company_context.company_products[i].name
                    assert product.description == expected_input.company_context.company_products[i].description

    @pytest.mark.parametrize(
        "user_email, messages, meta_agent_chunks, expected_outputs",
        [
            (
                "user@example.com",
                [ChatMessage(role="USER", content="Hello")],
                [
                    MetaAgentOutput(
                        messages=[ChatMessage(role="ASSISTANT", content="Hi there!")],
                    ),
                    MetaAgentOutput(
                        messages=[ChatMessage(role="ASSISTANT", content="How can I help you today?")],
                    ),
                ],
                [
                    [ChatMessage(role="ASSISTANT", content="Hi there!")],
                    [ChatMessage(role="ASSISTANT", content="How can I help you today?")],
                ],
            ),
            (
                None,
                [ChatMessage(role="USER", content="Help")],
                [
                    MetaAgentOutput(messages=None),  # Empty chunk
                    MetaAgentOutput(
                        messages=[ChatMessage(role="ASSISTANT", content="I can help with WorkflowAI!")],
                    ),
                ],
                [
                    [ChatMessage(role="ASSISTANT", content="I can help with WorkflowAI!")],
                ],
            ),
            (
                "user@example.com",
                [],  # Empty messages
                [],  # No chunks expected
                [
                    [
                        ChatMessage(
                            role="ASSISTANT",
                            content="Hey! I'm WorkflowAI's agent, you can ask me anything about the platform. How can I help you today?",
                        ),
                    ],
                ],
            ),
        ],
    )
    async def test_stream_meta_agent_response(
        self,
        user_email: str | None,
        messages: list[ChatMessage],
        meta_agent_chunks: list[MetaAgentOutput],
        expected_outputs: list[list[ChatMessage]],
    ) -> None:
        mock_storage = Mock(spec=BackendStorage)
        mock_event_router = Mock()
        service = MetaAgentService(storage=mock_storage, event_router=mock_event_router)

        # Create a mock for _build_meta_agent_input
        mock_input = MetaAgentInput(
            messages=messages,
            company_context=MetaAgentInput.CompanyContext(),
            workflowai_documentation="API Documentation",
        )

        # Create a mock for the stream response
        class MockStreamResponse(BaseModel):
            output: MetaAgentOutput

        # Patch the _build_meta_agent_input method
        with patch.object(
            service,
            "_build_meta_agent_input",
            new_callable=AsyncMock,
            return_value=mock_input,
        ) as mock_build_input:
            # Patch the meta_agent.stream function
            with patch(
                "api.services.internal_tasks.meta_agent_service.meta_agent.stream",
                return_value=mock_aiter(*[MockStreamResponse(output=chunk) for chunk in meta_agent_chunks]),
            ) as mock_stream:
                # Call the method and collect the results
                results = [chunk async for chunk in service.stream_meta_agent_response(user_email, messages)]

                # Verify the results match expected outputs
                assert results == expected_outputs

                # Verify _build_meta_agent_input was called or not based on messages
                if not messages:
                    mock_build_input.assert_not_called()
                    mock_stream.assert_not_called()
                else:
                    mock_build_input.assert_called_once_with(user_email, messages)

    @pytest.mark.parametrize(
        "input_messages, expected_messages",
        [
            (
                [
                    ChatMessage(role="ASSISTANT", content="A"),
                    ChatMessage(role="USER", content="User1"),
                    ChatMessage(role="USER", content="User2"),
                ],
                [
                    ChatMessage(role="USER", content="User1"),
                    ChatMessage(role="USER", content="User2"),
                ],
            ),
        ],
    )
    def test_dispatch_new_user_messages_event(
        self,
        input_messages: list[ChatMessage],
        expected_messages: list[ChatMessage],
    ) -> None:
        mock_event_router = Mock()

        service = MetaAgentService(storage=Mock(), event_router=mock_event_router)

        service.dispatch_new_user_messages_event(input_messages)

        mock_event_router.assert_called_once_with(MetaAgentChatMessagesSent(messages=expected_messages))
