from pydantic import BaseModel

from core.utils.hash import compute_model_hash


class HashableModel(BaseModel):
    def __hash__(self) -> int:
        return hash(compute_model_hash(self))
