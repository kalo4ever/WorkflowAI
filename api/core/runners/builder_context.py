from contextvars import ContextVar
from typing import Any, Optional, Protocol

from core.domain.llm_completion import LLMCompletion
from core.domain.task_run_reply import RunReply


class BuilderInterface(Protocol):
    @property
    def id(self) -> str: ...

    @property
    def llm_completions(self) -> list[LLMCompletion]: ...

    @property
    def reply(self) -> RunReply | None: ...

    def add_metadata(self, key: str, value: Any) -> None: ...

    def get_metadata(self, key: str) -> Any | None: ...

    def record_file_download_seconds(self, seconds: float) -> None: ...


builder_context = ContextVar[Optional[BuilderInterface]]("builder_context", default=None)
