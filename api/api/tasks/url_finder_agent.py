from typing import Any

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model


class URLFinderAgentInput(BaseModel):
    agent_name: str = Field(description="The name of the agent")
    agent_input_json_schema: dict[str, Any] = Field(description="The agent input JSON schema")


class URLFinderAgentOutput(BaseModel):
    is_schema_containing_url: bool = Field(description="Whether the 'input_json_schema' contains an URL field")


@workflowai.agent(model=Model.GEMINI_2_0_FLASH_001)
async def url_finder_agent(
    input: URLFinderAgentInput,
) -> URLFinderAgentOutput:
    """You are a specialist at spotting URL / website fields in JSON schemas.

    Your goal is to spot if the 'agent_input_json_schema' contains an URL field.

    Search for fields like "url", "website", "link", etc.
    Also consider that some fields might be nested.
    """
    ...
