import logging
from typing import Any

from pydantic import BaseModel


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

    def append(self, val: Any, cut_on_max_len: bool = True):
        s = self._stringify(val)
        if self.remaining < len(s):
            if cut_on_max_len:
                s = s[: self.remaining]
            self.agg.append(s)
            raise _MaxLenReached()
        self.agg.append(s)
        self.remaining -= len(s)
        if self.remaining == 0:
            raise _MaxLenReached()

    def __str__(self) -> str:
        return "".join(self.agg)

    def _append_any(self, value: Any):
        if isinstance(value, dict):
            self._append_dict(value, brackets=True)  # pyright: ignore [reportUnknownArgumentType]
        elif isinstance(value, list):
            self.append("[")
            self._append_list(value)  # pyright: ignore [reportUnknownArgumentType]
            self.append("]")
        elif isinstance(value, str):
            self.append(f'"{value}"')
        else:
            self.append(value)

    def _append_file(self, content_type: str, url: str | None, storage_url: str | None):
        if url and not url.startswith("https://"):
            url = storage_url
        if not url:
            url = ""

        match content_type.split("/")[0]:
            case "image":
                prefix = "img"
            case "audio":
                prefix = "audio"
            case _:
                prefix = "file"
        self.append(f"[[{prefix}:{url}]]", cut_on_max_len=False)

    def _append_dict(self, d: dict[str, Any], brackets: bool):
        # For simplification, we consider that any dict
        # with a "content_type" key is a file and should have a specific preview
        if "content_type" in d and ("url" in d or "data" in d or "storage_url" in d):
            self._append_file(d["content_type"], d.get("url"), d.get("storage_url"))
            return
        if brackets:
            self.append("{")

        for i, (k, v) in enumerate(d.items()):
            if i > 0:
                self.append(", ")
            self.append(k)
            self.append(": ")
            self._append_any(v)

        if brackets:
            self.append("}")

    def _append_list(self, arr: list[Any]):
        for i, v in enumerate(arr):
            if i > 0:
                self.append(", ")
            self._append_any(v)

    def build(self, value: Any):
        try:
            # Not use _any_preview to avoid adding quotes to strings, etc.
            if isinstance(value, dict):
                self._append_dict(value, brackets=False)  # type: ignore
            elif isinstance(value, list):
                self._append_list(value)  # type: ignore
            else:
                self.append(value)
        except _MaxLenReached:
            pass

        return str(self)


def compute_preview(model: Any, max_len: int = 255) -> str:
    """Compute a preview for a given object. All exceptions are handled and a fallback is returned."""
    if not model:
        return "-"

    if isinstance(model, BaseModel):
        model = model.model_dump(exclude_none=True, mode="json")

    try:
        return _Agg(max_len).build(model)
    except Exception:
        logging.getLogger(__name__).exception("error computing preview", extra={"model": model})
        return "..."
