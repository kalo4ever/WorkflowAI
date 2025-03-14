from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


# TODO: we should remove this class as it no longer serves a purpose
class EvaluatorOptions(BaseModel):
    """
    Specify how a task will be evaluated
    """

    model_config = ConfigDict(extra="allow")

    # The name of the evaluator that will be used
    name: str = ""

    @classmethod
    def default_name(cls) -> str:
        return cls.__name__.removesuffix("EvaluatorOptions")

    @model_validator(mode="after")
    def set_default_name(self) -> Self:
        if not self.name:
            self.name = self.default_name()
        return self
