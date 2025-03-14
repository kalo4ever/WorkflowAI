from typing import Any

from pydantic import BaseModel
from typing_extensions import override

from core.domain.task_variant import SerializableTaskVariant
from core.runners.abstract_runner import AbstractRunner


class DummyRunnerOptions(BaseModel):
    pass


class DummyRunner(AbstractRunner[DummyRunnerOptions]):
    @override
    def version(self) -> str:
        return "dummy"

    @override
    async def _build_task_output(self, input: Any) -> Any:
        return {}

    @classmethod
    @override
    def supports(cls, task: SerializableTaskVariant) -> bool:
        return True

    @classmethod
    @override
    def options_class(cls) -> type[Any]:
        return DummyRunnerOptions
