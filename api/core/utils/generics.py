from typing import TypeVar

from pydantic import BaseModel

# A basic generic type variable
T = TypeVar("T")

BM = TypeVar("BM", bound=BaseModel)
