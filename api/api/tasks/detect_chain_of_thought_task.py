from typing import Any

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model


class DetectChainOfThoughtUsageTaskInput(BaseModel):
    task_output_schema: dict[str, Any]
    task_instructions: str


class DetectChainOfThoughtUsageTaskOutput(BaseModel):
    should_use_chain_of_thought: bool = Field(
        default=False,
        description="Wether the task_instructions suggest that the task should use chain of thought reasoning",
    )


@workflowai.agent(id="detect-chain-of-thought", model=Model.GEMINI_1_5_PRO_002)
async def run_detect_chain_of_thought_task(
    input: DetectChainOfThoughtUsageTaskInput,
) -> DetectChainOfThoughtUsageTaskOutput:
    """Analyze the given 'task_instructions' and 'task_output_schema' to determine if they suggest the use of using chain of thought reasoning.

    Only return 'should_use_chain_of_thought=true' if the 'task_instructions' explicitelly ask for "think step by step", "using COT", "using chain of thoughts" or similar sentence requiring explicit reasoning.

    Importantly, only return 'should_use_chain_of_thought=true' if the 'task_output_schema' does not already contains fields that are made to store reasoning steps, reasons, etc."""
    ...
