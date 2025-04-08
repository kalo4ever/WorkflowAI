import logging
from typing import Any, AsyncIterator

from pydantic import Field
from typing_extensions import Literal

from api.services.internal_tasks.internal_tasks_service import InternalTasksService
from api.services.tasks import list_agent_summaries
from core.agents.agent_input_output_example import (
    SuggestedAgentInputOutputExampleInput,
    SuggestedAgentInputOutputExampleOutput,
    stream_suggested_agent_input_output_example,
)
from core.agents.chat_task_schema_generation.chat_task_schema_generation_task import (
    AgentBuilderInput,
    ChatMessageWithExtractedURLContent,
    InputSchemaFieldType,
    OutputSchemaFieldType,
    agent_builder,
)
from core.agents.chat_task_schema_generation.chat_task_schema_generation_task_utils import build_json_schema_with_defs
from core.agents.detect_company_domain_task import (
    DetectCompanyDomainTaskInput,
    run_detect_company_domain_task,
)
from core.agents.extract_company_info_from_domain_task import (
    safe_extract_company_domain,
    safe_generate_company_description_from_domain,
)
from core.agents.suggest_llm_features_for_company_agent import (
    AgentSuggestionChatMessage,
    SuggestedAgent,
    SuggestLlmAgentForCompanyInput,
    SuggestLlmAgentForCompanyOutput,
    suggest_llm_agents_for_company,
)
from core.runners.workflowai.workflowai_runner import WorkflowAIRunner
from core.storage.backend_storage import BackendStorage
from core.utils.iter_utils import safe_map


def get_supported_task_input_types() -> list[str]:
    return [type.value for type in InputSchemaFieldType] + ["enum", "array", "object"]


def get_supported_task_output_types() -> list[str]:
    return [type.value for type in OutputSchemaFieldType] + ["enum", "array", "object"]


class SuggestLlmAgentsForCompanyOutputAndStatus(SuggestLlmAgentForCompanyOutput):
    status: Literal["extracting_company_domain", "analyzing_company_context", "generating_agent_suggestions"]


class SuggestedAgentOutputExampleOutputWithSchema(SuggestedAgentInputOutputExampleOutput):
    agent_input_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema of the agent input",
    )
    agent_output_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema of the agent output",
    )


class TaskSuggestionsService:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def stream_agent_suggestions(
        self,
        messages: list[AgentSuggestionChatMessage] | None,
        storage: BackendStorage | None,
        user_email: str | None = None,
    ) -> AsyncIterator[SuggestLlmAgentsForCompanyOutputAndStatus]:
        if messages is None:
            messages = []

        if not user_email:
            # Extract company domain from messages
            yield SuggestLlmAgentsForCompanyOutputAndStatus(
                status="extracting_company_domain",
            )

            detect_company_domain_output = await run_detect_company_domain_task(
                DetectCompanyDomainTaskInput(messages=[message.to_chat_message() for message in messages]),
            )

            if not detect_company_domain_output.company_domain:
                yield SuggestLlmAgentsForCompanyOutputAndStatus(
                    status="extracting_company_domain",
                    assistant_message=AgentSuggestionChatMessage(
                        role="ASSISTANT",
                        content_str=detect_company_domain_output.failure_assistant_answer
                        or "Please provide your company domain",  # fallback message
                    ),
                )
                return
            company_domain = detect_company_domain_output.company_domain
        else:
            # Extract company domain from user email
            company_domain = await safe_extract_company_domain(user_email)

        yield SuggestLlmAgentsForCompanyOutputAndStatus(
            status="analyzing_company_context",
        )

        company_description = await safe_generate_company_description_from_domain(company_domain)

        yield SuggestLlmAgentsForCompanyOutputAndStatus(
            status="generating_agent_suggestions",
        )

        agent_suggestion_input = SuggestLlmAgentForCompanyInput(
            supported_agent_input_types=get_supported_task_input_types(),
            supported_agent_output_types=get_supported_task_output_types(),
            available_tools=safe_map(
                WorkflowAIRunner.internal_tools.values(),
                SuggestLlmAgentForCompanyInput.ToolDescription.from_internal_tool,
            ),
            company_context=SuggestLlmAgentForCompanyInput.CompanyContext(
                company_name=company_description.company_name if company_description else None,
                company_description=company_description.model_dump_json() if company_description else None,
                # We can only feed the existing agents if the user is authenticated
                existing_agents=[str(a) for a in await list_agent_summaries(storage)] if storage else [],
            ),
            messages=messages,
        )

        async for chunk in suggest_llm_agents_for_company(agent_suggestion_input):
            yield SuggestLlmAgentsForCompanyOutputAndStatus(
                status="generating_agent_suggestions",
                assistant_message=chunk.assistant_message,
            )

    async def stream_agent_output_preview(
        self,
        suggested_agent: SuggestedAgent | None,
    ) -> AsyncIterator[SuggestedAgentInputOutputExampleOutput]:
        if suggested_agent is None:
            return
        agent_schema_gen_message = f"""{suggested_agent.agent_description}
{suggested_agent.explanation}
Input: {suggested_agent.input_specifications}
Output: {suggested_agent.output_specifications}
"""

        agent_schema_gen_output = await agent_builder(
            # User content is omitted here for latency reasons, this endpoint needs to be fast
            AgentBuilderInput(
                previous_messages=[],
                new_message=ChatMessageWithExtractedURLContent(role="USER", content=agent_schema_gen_message),
            ),
            use_cache="always",
        )

        input_schema = (
            build_json_schema_with_defs(agent_schema_gen_output.new_agent_schema.input_schema)
            if agent_schema_gen_output.new_agent_schema
            else None
        )
        output_schema = (
            build_json_schema_with_defs(agent_schema_gen_output.new_agent_schema.output_schema)
            if agent_schema_gen_output.new_agent_schema
            else None
        )

        if output_schema:
            output_schema = InternalTasksService.add_explanation_to_schema_if_needed(output_schema, self._logger)

        agent_output_example_input = SuggestedAgentInputOutputExampleInput(
            agent_description=suggested_agent.agent_description,
            explaination=suggested_agent.explanation,
            destination_department=suggested_agent.department,
            input_json_schema=input_schema,
            output_json_schema=output_schema,
        )
        async for chunk in stream_suggested_agent_input_output_example(agent_output_example_input):
            yield SuggestedAgentOutputExampleOutputWithSchema(
                **chunk.model_dump(),
                agent_input_schema=input_schema,
                agent_output_schema=output_schema,
            )
