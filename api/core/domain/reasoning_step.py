from pydantic import BaseModel, Field

INTERNAL_REASONING_STEPS_SCHEMA_KEY = "internal_reasoning_steps"


class ReasoningStep(BaseModel):
    step_number: int = Field(description="The step number")
    description: str = Field(description="The description of the reasoning step")
    output: str = Field(description="The output of the step")
