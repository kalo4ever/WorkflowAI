from typing import Any, Literal

type CacheUsage = Literal["auto", "always", "never", "when_available", "only"]
# when_available & only are deprecated

type TaskInputDict = dict[str, Any]
type TaskOutputDict = dict[str, Any]
