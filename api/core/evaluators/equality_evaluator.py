from typing import Any

from typing_extensions import override

from core.domain.evaluator_options import EvaluatorOptions

from .example_based_evaluator import ExampleBasedEvaluator


class EqualityEvaluator(ExampleBasedEvaluator["EqualityEvaluatorOptions"]):
    """
    An evaluator that compares outputs using the equality operator
    """

    @override
    def _version(self) -> str:
        return "1.0.0"

    @override
    async def _compute_score(
        self,
        run_output: dict[str, Any],
        example_output: dict[str, Any],
        input: dict[str, Any],
    ) -> tuple[float, str]:
        return float(run_output == example_output), ""

    @classmethod
    def options_class(cls) -> type["EqualityEvaluatorOptions"]:
        return EqualityEvaluatorOptions


class EqualityEvaluatorOptions(EvaluatorOptions):
    name: str = "Equality"
