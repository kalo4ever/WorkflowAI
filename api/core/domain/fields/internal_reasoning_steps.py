from pydantic import BaseModel, Field


class InternalReasoningStep(BaseModel):
    title: str | None = Field(default=None, description="A brief title for this step (maximum a few words)")
    explaination: str | None = Field(default=None, description="The explanation for this step of reasoning")
    output: str | None = Field(default=None, description="The output or conclusion from this step")

    def append_explanation(self, explanation: str):
        if not self.explaination:
            self.explaination = ""
        self.explaination += explanation
