from contextvars import ContextVar
from typing import Optional

request_id_var = ContextVar[Optional[str]]("request_id", default=None)
