from enum import Enum
from typing import Optional

import workflowai
from pydantic import BaseModel
from workflowai import Model, Run


class EvaluateOutputTaskInput(BaseModel):
    task_input: Optional[str] = None
    correct_outputs: Optional[list[str]] = None
    incorrect_outputs: Optional[list[str]] = None
    evaluation_instruction: Optional[str] = None
    input_evaluation_instruction: Optional[str] = None
    evaluated_output: Optional[str] = None


class EvaluationResult(Enum):
    positive = "positive"
    negative = "negative"
    unsure = "unsure"

    def to_score(self) -> float:
        if self == EvaluationResult.positive:
            return 1.0
        if self == EvaluationResult.negative:
            return 0.0
        return 0.5


class EvaluateOutputTaskOutput(BaseModel):
    evaluation_result: Optional[EvaluationResult] = None
    confidence_score: Optional[float] = None
    positive_aspects: Optional[list[str]] = None
    negative_aspects: Optional[list[str]] = None


@workflowai.agent(id="evaluate-output", model=Model.O1_MINI_2024_09_12)
async def evaluate_output(input: EvaluateOutputTaskInput) -> Run[EvaluateOutputTaskOutput]:
    """Evaluate the given output against the correct and incorrect examples, considering the task input and evaluation instructions.

    Provide the evaluation result, which should be either:
    - 'positive'
    - 'negative'
    - or 'unsure'.

    Also, include a confidence score between 0 and 1, where 0 means no confidence and 1 means full confidence.

    List the positive and negative aspects of the evaluated output:

    - Provide a list for each aspect in the respective lists.
    - Focus on the content and relevance of the output.
    - Do not include any general statements about the output's format or validity.
    - If there are no positive aspects, leave the 'positive_aspects' list empty.
    - If there are no negative aspects, leave the 'negative_aspects' list empty.
    - Each aspect should be a separate string in the list.
    - Do not include any headers or additional formatting within the list items.

    Consider semantic similarity, synonyms, nicknames, or alternative names in your evaluation.

    "The evaluated output is a valid JSON object." must not be considered a positive aspect."""
    ...
