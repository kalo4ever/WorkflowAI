import os
from typing import Literal, cast

WORKFLOWAI_ENV_FOR_INTERNAL_TASKS = cast(
    Literal["production", "staging", "dev"],
    os.getenv(
        "WORKFLOWAI_ENV_FOR_INTERNAL_TASKS",
        "production",
    ),
)
