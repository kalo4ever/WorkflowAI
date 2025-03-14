from typing import Any, TypeAlias

from core.domain.error_response import ErrorCode
from core.domain.errors import InternalError


class ObjectNotFoundException(InternalError):
    code: ErrorCode = "object_not_found"

    def __init__(self, msg: str | None = None, code: ErrorCode | None = None, **extras: Any):
        super().__init__(msg, **extras)
        self.code = code or self.code
        self.extras = extras or {}


# TODO[ids]: passing as a tuple for now to reduce the amount of changes needed
# We should eventually  only use the int
TenantTuple: TypeAlias = tuple[str, int]
TaskTuple: TypeAlias = tuple[str, int]
