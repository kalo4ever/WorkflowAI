import workflowai
from pydantic import BaseModel, Field

from api.tasks.meta_agent import MetaAgentChatMessage
from core.domain.documentation_section import DocumentationSection


class PickRelevantDocumentationSectionsInput(BaseModel):
    available_doc_sections: list[DocumentationSection] = Field(description="The available documentation sections.")
    chat_messages: list[MetaAgentChatMessage] = Field(
        description="The chat messages between the user and the assistant.",
    )
    agent_instructions: str = Field(description="The agent's internal instructions.")


class PickRelevantDocumentationSectionsOutput(BaseModel):
    relevant_doc_sections: list[str] = Field(description="The relevant documentation sections for the agent.")


@workflowai.agent(model=workflowai.Model.GEMINI_2_0_FLASH_001)
async def pick_relevant_documentation_sections(
    input: PickRelevantDocumentationSectionsInput,
) -> PickRelevantDocumentationSectionsOutput:
    """
    You are an expert at picking relevant docucmentation sections for other agents.

    Your goal is to analyze the chat history and the agent's instructions, and pick the most relevant documentation sections from the 'available_doc_sections' list.
    You must at the same time pick the required documentation sections for the agent, but avoid picking too unnecessary sections.
    Unnecessary sections are, for example:
    - things that the agent already knows about based on the 'agent_instructions'
    - things that are not related to the matters discussed in the 'chat_messages'
    """
    ...
