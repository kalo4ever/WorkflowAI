import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, Optional, TypeVar, overload

from core.domain.errors import ExampleNotFoundError, TaskRunHasNoExampleError
from core.domain.evaluator_options import EvaluatorOptions
from core.domain.task_evaluation import TaskEvaluation
from core.domain.task_example import SerializableTaskExample
from core.domain.task_run import Run
from core.storage import ObjectNotFoundException

EvaluatorOptionsVar = TypeVar("EvaluatorOptionsVar", bound=EvaluatorOptions)


# Raised when the confidence score is not high enough
# Evaluation should be discarded
class InvalidEvaluationError(Exception):
    pass


class AbstractEvaluator(ABC, Generic[EvaluatorOptionsVar]):
    def __init__(self, options: dict[str, Any] | EvaluatorOptionsVar | None = None):
        if isinstance(options, EvaluatorOptions):
            self.options: EvaluatorOptionsVar = options
        else:
            self.options: EvaluatorOptionsVar = self.build_options(options)
        self._definition: Optional["TaskEvaluation.Evaluator"] = None
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def definition(self) -> "TaskEvaluation.Evaluator":
        if not self._definition:
            raise ValueError("Evaluator ID not set. Has prepare been called?")
        return self._definition

    def _definition_id(self):
        return f"{self.name()}/{self._version()}"

    # TODO: definition should be computed before the evaluator is initialized
    # cf faithfulness_evaluator.py and field_based_compare.py
    async def prepare(self) -> "TaskEvaluation.Evaluator":
        """Prepare the evaluator for evaluation.
        This method is called before the evaluation starts.
        Custom implementation should at least set the _definition property"""
        if self._definition:
            return self._definition

        self._definition = TaskEvaluation.Evaluator(
            name=self.name(),
            id=self._definition_id(),
            properties=self._evaluator_properties(),
        )
        return self._definition

    @abstractmethod
    def _version(self) -> str:
        """Return a version string for the evaluator. The version is used in prepare to set the definition"""
        pass

    @classmethod
    def name(cls) -> str:
        return cls.__name__.removesuffix("Evaluator")

    def can_evaluate(self, run: Run) -> bool:
        """Check if the evaluator can evaluate the given run"""
        if self.requires_example():
            return run.example_id is not None
        return True

    def _evaluator_properties(self) -> dict[str, Any]:
        """Returns properties that will be attached to the evaluation"""
        return self.options.model_dump(exclude_none=True, exclude={"name"})

    @abstractmethod
    async def evaluate(
        self,
        run: Run,
        example: Optional[SerializableTaskExample] = None,
    ) -> "TaskEvaluation":
        """Base method for evaluation. Responsible for building a TaskEvaluation object.

        Args:
            run (Run): a task run
            example (Optional[SerializableTaskExample], optional): An optional example. Defaults to None.

        Returns:
            TaskEvaluation: The evaluation object with the score, evaluator_id and other metadata
        """
        pass

    @classmethod
    def options_class(cls) -> type[EvaluatorOptionsVar]:
        """
        A class that defines the options for the evaluator.
        The option class will be instantiated based on user or API input, passed
        to the _build_task_output function and stored in the task run metadata.
        """
        return EvaluatorOptions  # type: ignore

    @classmethod
    def build_options(cls, options: Optional[dict[str, Any]]) -> EvaluatorOptionsVar:
        """
        Build the evaluator options from a dictionary.
        """
        if options is None:
            return cls.options_class().model_validate({})
        if "name" not in options:
            options["name"] = cls.name()
        return cls.options_class().model_validate(options)

    def requires_example(self) -> bool:
        """Whether the evaluator requires an example to evaluate a task run. Defaults to false"""
        return False

    @overload
    async def fetch_example(
        self,
        run: Run,
        required: Literal[True],
    ) -> SerializableTaskExample: ...

    @overload
    async def fetch_example(
        self,
        run: Run,
        required: bool,
    ) -> SerializableTaskExample | None: ...

    async def fetch_example(
        self,
        run: Run,
        required: bool = True,
    ) -> SerializableTaskExample | None:
        if not run.example_id:
            if required:
                raise TaskRunHasNoExampleError(f"Examples are required by {self.name()}")
            return None

        from core.deprecated.workflowai import WorkflowAI

        wai = WorkflowAI.from_ctx()

        try:
            return await wai.storage.example_resource_by_id(run.example_id)
        except ObjectNotFoundException:
            if required:
                raise ExampleNotFoundError(f"Example with id {run.example_id} not found")
            return None
