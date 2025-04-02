from enum import Enum

from pydantic import BaseModel, Field

from core.domain.deprecated.task import Task


class ChatFaithfulnessCheckTaskInput(BaseModel):
    new_user_message: str = Field(description="The message from the user.")
    new_assistant_answer: str = Field(description="The actual answer from the assistant.")
    expert_answer: str = Field(description="The ideal answer from the expert.")


class ChatFaithfulnessCheckTaskOutput(BaseModel):
    class FaithfulnessCategory(Enum):
        A = "A"
        B = "B"
        C = "C"
        D = "D"

    faithfulness_category: FaithfulnessCategory

    reason: str = Field(description="The reason for the faithfulness category.")


class ChatFaithfulnessCheckTask(Task[ChatFaithfulnessCheckTaskInput, ChatFaithfulnessCheckTaskOutput]):
    input_class: type[ChatFaithfulnessCheckTaskInput] = ChatFaithfulnessCheckTaskInput
    output_class: type[ChatFaithfulnessCheckTaskOutput] = ChatFaithfulnessCheckTaskOutput
    instructions: str = """Compare the factual content of the 'new_assistant_answer' with the 'expert_answer'. Ignore any differences in style, grammar, or punctuation.
    The 'new_assistant_answer' may either be a subset or superset of the 'expert_answer', or it may conflict with it. Determine which case applies. Answer the question by selecting one of the following options:
    (A) The 'new_assistant_answer' is a subset of the 'expert_answer' and is fully consistent with it.
    (B) The 'new_assistant_answer' is a superset of the 'expert_answer' and is fully consistent with it.
    (C) There is a disagreement between the 'new_assistant_answer' and the 'expert_answer'.
    (D) The 'new_assistant_answer' contains all the same details as the 'expert_answer', with possible formulation differences that do not matter from the perspective of factuality..
"""
