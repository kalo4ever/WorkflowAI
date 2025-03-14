import workflowai
from pydantic import BaseModel, Field

from api.tasks.extract_company_info_from_domain_task import Product
from core.domain.fields.chat_message import ChatMessage


class MetaAgentInput(BaseModel):
    messages: list[ChatMessage] = Field(
        description="The list of messages in the conversation, the last message being the most recent one",
    )

    class CompanyContext(BaseModel):
        company_name: str | None = None
        company_description: str | None = None
        company_locations: list[str] | None = None
        company_industries: list[str] | None = None
        company_products: list[Product] | None = None
        current_agents: list[str] | None = Field(
            default=None,
            description="The list of existing agents for the company",
        )

    company_context: CompanyContext = Field(
        description="The context of the company to which the conversation belongs",
    )

    workflowai_documentation: str = Field(
        description="The documentation of the WorkflowAI platform, which this agent is part of",
    )


class MetaAgentOutput(BaseModel):
    messages: list[ChatMessage] | None = Field(
        default=None,
        description="The list of messages that compose the response of the meta-agent",
    )


@workflowai.agent(
    model=workflowai.Model.GPT_4O_2024_11_20,
)
async def meta_agent(_: MetaAgentInput) -> MetaAgentOutput:
    """You are WorkflowAI's meta-agent. You are responsible for helping WorkflowAI's users succeed in their goals using the WorkflowAI platform.

    Solely answer user's questions based on the 'workflowai_documentation' and the 'company_context'.

    Do not use markdown in your answers.
    """
    ...
