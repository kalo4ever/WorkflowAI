# Install the SDK
from enum import StrEnum
from typing import List, Optional

import workflowai
from pydantic import BaseModel
from workflowai import Model


class PreviousEvaluationResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNSURE = "UNSURE"


class UpdateCorrectOutputsAndInstructionsTaskInput(BaseModel):
    evaluation_instruction: Optional[str] = None
    evaluated_output: Optional[str] = None
    evaluation_result: Optional[PreviousEvaluationResult] = None
    correct_outputs: Optional[List[str]] = None
    incorrect_outputs: Optional[List[str]] = None
    why_is_the_evaluated_output_also_correct: Optional[str] = None
    why_is_the_evaluated_output_incorrect: Optional[str] = None


class UpdateCorrectOutputsAndInstructionsTaskOutput(BaseModel):
    updated_correct_outputs: Optional[List[str]] = None
    updated_incorrect_outputs: Optional[List[str]] = None
    updated_evaluation_instruction: Optional[str] = None
    update_evaluation_instruction_for_input: Optional[str] = None


@workflowai.agent(id="update-correct-outputs-and-instructions", model=Model.O1_PREVIEW_2024_09_12)
async def update_correct_outputs_and_instructions(
    input: UpdateCorrectOutputsAndInstructionsTaskInput,
) -> workflowai.Run[UpdateCorrectOutputsAndInstructionsTaskOutput]:
    """You are supposed to correct the evaluation of a task that converts an input into and output. The previous evaluation failed and the user provided a possible feedback.

    - Update the correct outputs and incorrect outputs as needed
    - Modify the evaluation instructions if necessary. Separating ones that could affect all inputs instead and just the current one"""
    ...
