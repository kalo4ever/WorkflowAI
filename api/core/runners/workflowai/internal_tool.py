from collections.abc import Callable
from typing import Any, NamedTuple

from core.domain.tool import Tool
from core.tools import ToolKind
from core.utils.tool_utils.tool_utils import build_tool, get_tool_for_tool_kind


class InternalTool(NamedTuple):
    definition: Tool
    fn: Callable[..., Any]

    @classmethod
    def from_tool_kind(cls, tool_kind: ToolKind):
        tool_fn = get_tool_for_tool_kind(tool_kind)
        return cls(definition=build_tool(tool_kind.value, tool_fn), fn=tool_fn)


def build_all_internal_tools() -> dict[ToolKind, InternalTool]:
    return {k: InternalTool.from_tool_kind(k) for k in ToolKind}
