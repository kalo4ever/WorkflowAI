from typing import Any

from pydantic import BaseModel, RootModel


class _MaxLenReached(Exception):
    pass


class _Agg:
    def __init__(self, remaining: int):
        self.agg: list[str] = []
        self.remaining = remaining

    def _stringify(self, value: Any) -> str:
        if isinstance(value, float):
            return f"{round(value, 2)}".rstrip("0").rstrip(".")
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value).replace("\n", " ")

    def append(self, val: Any):
        s = self._stringify(val)
        if self.remaining < len(s):
            self.agg.append(s[: self.remaining])
            raise _MaxLenReached()
        self.agg.append(s)
        self.remaining -= len(s)
        if self.remaining == 0:
            raise _MaxLenReached()

    def __str__(self) -> str:
        return "".join(self.agg)


def _any_preview(value: Any, agg: _Agg):
    if isinstance(value, dict):
        agg.append("{")
        _dict_preview(value, agg)  # type: ignore
        agg.append("}")
    elif isinstance(value, list):
        agg.append("[")
        _list_preview(value, agg)  # type: ignore
        agg.append("]")
    elif isinstance(value, str):
        agg.append(f'"{value}"')
    else:
        agg.append(value)


def _dict_preview(d: dict[str, Any], agg: _Agg):
    for i, (k, v) in enumerate(d.items()):
        if i > 0:
            agg.append(", ")
        agg.append(k)
        agg.append(": ")
        _any_preview(v, agg)


def _list_preview(arr: list[Any], agg: _Agg):
    for i, v in enumerate(arr):
        if i > 0:
            agg.append(", ")
        _any_preview(v, agg)


def compute_preview(model: Any, max_len: int = 255) -> str:
    if not model:
        return "-"

    if not isinstance(model, BaseModel):
        model = RootModel(model)

    dumped = model.model_dump(exclude_none=True, mode="json")

    agg = _Agg(max_len)
    try:
        # Not use _any_preview to avoid adding quotes to strings, etc.
        if isinstance(dumped, dict):
            _dict_preview(dumped, agg)  # type: ignore
        elif isinstance(dumped, list):
            _list_preview(dumped, agg)  # type: ignore
        else:
            agg.append(dumped)
    except _MaxLenReached:
        pass
    return str(agg)
