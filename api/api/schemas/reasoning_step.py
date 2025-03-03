from pydantic import BaseModel

from core.domain.fields.internal_reasoning_steps import InternalReasoningStep


class ReasoningStep(BaseModel):
    title: str | None
    step: str | None

    @classmethod
    def from_domain(cls, step: InternalReasoningStep):
        return cls(title=step.title, step=step.explaination)
