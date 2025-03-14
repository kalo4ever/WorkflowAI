from typing import Any, AsyncIterator

import workflowai
from pydantic import BaseModel, Field


class SuggestedAgentOutputExampleInput(BaseModel):
    agent_name: str | None = Field(
        default=None,
        description="The name of the agent",
    )
    agent_description: str | None = Field(
        default=None,
        description="The public description of the agent",
    )
    agent_specifications: str | None = Field(
        default=None,
        description="The private specifications of the agent, describes the agent input and output",
    )
    company_context: str | None = Field(
        default=None,
        description="The context of the company that will run the agent, to use to generate a realistic output",
    )


class SuggestedAgentOutputExampleOutput(BaseModel):
    agent_output_example: dict[str, Any] | None = Field(
        default=None,
        description="An example that illustrates the agent output (enforcing the 'agent_output_schema')",
    )


@workflowai.agent(id="suggested-task-output-example", model=workflowai.Model.GEMINI_2_0_FLASH_001)
def stream_suggested_agent_output_example(
    input: SuggestedAgentOutputExampleInput,
) -> AsyncIterator[SuggestedAgentOutputExampleOutput]:
    """You are a specialist in generating realistic examples for agent output.

    Your goal is to analyze the input data containing:

    - an agent name
    - an agent description
    - an agent specifications (optional)
    - a company context (optional)

    Based on the context above, you must generate an example output that illustrates the agent output.
    When generating the output, take into account the 'company_context', if present, to generate a realistic output.
    WARNING: Be very careful about ONLY outputting field that belongs to the output of the agent NOT the input

    # Examples

    ## Example 1:
    agent description: Identifies and explains food additives in products, categorizing them by risk level and providing evidence-based information about potential health impacts.
    agent_output_example:
    {
        "food_additives": [
            {
                "name": "Erythorbate",
                "risk_level": "Low",
                "risk_description": "Erythorbate is a food additive that is used to prevent the growth of bacteria and mold in food products. It is a synthetic antioxidant that is derived from the fermentation of glucose.",
                "sources": [
                    "https://www.fda.gov/food/food-additives-pet-food/food-additives-and-pet-food",
                    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3540419/"
                ]
            }
        ]
    }

    As you can see, the output only contains fields that are part of the output of the agent, not the input, no 'product_name' for example.

    """
    ...
