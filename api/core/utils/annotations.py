from collections.abc import Sequence
from typing import Annotated, Any, Union, get_args, get_origin


def get_type_annotations(cls: Any) -> Sequence[Any]:
    origin = get_origin(cls)
    if origin == Union:
        return get_type_annotations(get_args(cls)[0])
    if origin == Annotated:
        return get_args(cls)[1:]
    return []
