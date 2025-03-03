import json
from typing import Any


def compute_tags(data: dict[str, Any], max_len: int = 50) -> list[str]:
    """Compute tags from a dict"""

    def _stringify(value: Any):
        if isinstance(value, float):
            return f"{round(value, 2)}".rstrip("0").rstrip(".")
        if isinstance(value, str):
            return str(value)
        return json.dumps(value, sort_keys=True)

    out: list[str] = []
    for key, value in sorted(data.items()):
        if value is None:
            continue
        stringified = _stringify(value)[:max_len]
        if not stringified:
            continue
        out.append(f"{key}={stringified}")

    return out
