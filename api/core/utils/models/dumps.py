import json
from collections.abc import Mapping, Sequence
from logging import getLogger
from typing import Any

from pydantic import BaseModel

logger = getLogger(__name__)


def _dump_pydantic_model(model: Any) -> Any:
    if model is None:
        return None

    try:
        json.dumps(model)
        return model
    except TypeError:
        pass

    if isinstance(model, BaseModel):
        return model.model_dump(exclude_none=True)

    if isinstance(model, Mapping):
        return {k: _dump_pydantic_model(v) for k, v in model.items()}  # pyright: ignore [reportUnknownVariableType]

    if isinstance(model, Sequence):
        return [_dump_pydantic_model(v) for v in model]  # pyright: ignore [reportUnknownVariableType]

    raise ValueError(f"Unsupported model type: {type(model)}")


def safe_dump_pydantic_model(model: Any) -> Any:
    try:
        return _dump_pydantic_model(model)
    except Exception as e:
        logger.exception("Error dumping pydantic model", exc_info=e)
        return None
