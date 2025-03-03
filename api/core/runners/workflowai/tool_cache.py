import asyncio
from collections.abc import Iterable
from typing import Any

from core.domain.tool_call import ToolCall, ToolCallRequest, ToolCallRequestWithID
from core.utils.hash import compute_obj_hash


class ToolCache:
    def __init__(self):
        self._cache: dict[str, ToolCall] = {}
        self._lock = asyncio.Lock()

    def _serialize_args(self, args: dict[str, Any]) -> str:
        return compute_obj_hash(args)

    def _cache_key(self, name: str, args: dict[str, Any]) -> str:
        return f"{name}:{self._serialize_args(args)}"

    async def set(self, name: str, args: dict[str, Any], result: Any) -> None:
        async with self._lock:
            self._cache[self._cache_key(name, args)] = ToolCall(
                tool_name=name,
                tool_input_dict=args,
                result=result,
            )

    async def get(self, name: str, args: dict[str, Any]) -> ToolCall | None:
        async with self._lock:
            return self._cache.get(self._cache_key(name, args))

    async def values(self) -> list[ToolCall]:
        async with self._lock:
            return list(self._cache.values())

    async def ingest(self, calls: Iterable[ToolCallRequest] | None):
        if not calls:
            return

        async with self._lock:
            for call in calls:
                result = ToolCall(
                    tool_name=call.tool_name,
                    tool_input_dict=call.tool_input_dict,
                    result=None,
                )

                # If the provider returns a tool call with an ID (ex: OpenAI yes, Gemini no), we use it
                if type(call) is ToolCallRequestWithID:
                    result.id = call.id

                self._cache[self._cache_key(call.tool_name, call.tool_input_dict)] = result
