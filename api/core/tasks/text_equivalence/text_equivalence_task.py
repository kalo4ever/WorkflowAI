from typing import Optional

from pydantic import BaseModel, Field

from core.domain.deprecated.task import Task


class TextEquivalenceTaskInput(BaseModel):
    correct_text: str
    candidate_text: str


class TextEquivalenceTaskOutput(BaseModel):
    reason_not_equivalent: Optional[str] = Field(
        description="The reason why the two texts are not equivalent. Only present if the texts are not equivalent.",
    )
    are_texts_functionally_equivalent: bool


class TextEquivalenceTask(Task[TextEquivalenceTaskInput, TextEquivalenceTaskOutput]):
    input_class: type[TextEquivalenceTaskInput] = TextEquivalenceTaskInput
    output_class: type[TextEquivalenceTaskOutput] = TextEquivalenceTaskOutput

    instructions: str = """# Instructions

Assess whether the "candidate_text" contradicts with "correct_text".

If "candidate_text" contains less info than "correct_text" but do not contradicts with "correct_text", then output  are_texts_functionally_equivalent=true

If "candidate_text" contains more info than "correct_text" but do not contradicts with "correct_text", then output  are_texts_functionally_equivalent=true

If "candidate_text" contains the same info than "correct_text" but differs in wording, spelling, abreviations, etc. , then output  are_texts_functionally_equivalent=true

If "candidate_text" and "correct_text" are stricly equal, then output  are_texts_functionally_equivalent=true

If  "candidate_text" and "correct_text" talks about unrelated subjects or contradicts themselves, then output  are_texts_functionally_equivalent=false

Do not evaluate truthfulness of texts, just make sure they do not contradict, extrapolation, generalisation, more spercifity, in either of the text is fine.

# Examples

correct_text: "A journey of a thousand miles begins with a single step."
candidate_text: "A journey of a thousand miles begins with one step."
are_texts_functionally_equivalent: true

correct_text: "All that glitters is not gold."
candidate_text: "Not all that glitters is gold."
are_texts_functionally_equivalent: true

correct_text: "To be, or not to be, that is the question."
candidate_text: "To exist or not to be, that is the question."
are_texts_functionally_equivalent: true

correct_text: Restaurant recommendation
candidate_text: Best restaurants in the city
are_texts_functionally_equivalent: true"""
