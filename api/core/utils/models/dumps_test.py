from unittest.mock import Mock, patch

from pydantic import BaseModel

from .dumps import _dump_pydantic_model, safe_dump_pydantic_model  # pyright: ignore[reportPrivateUsage]


class _Model(BaseModel):
    a: int
    b: str | None = None


class TestPydanticModel:
    def test_dump_model(self) -> None:
        model = _Model(a=1, b="test")
        assert _dump_pydantic_model(model) == {"a": 1, "b": "test"}

    def test_dump_model_with_none(self) -> None:
        model = _Model(a=1)
        assert _dump_pydantic_model(model) == {"a": 1}

    def test_array_of_models(self) -> None:
        model = [_Model(a=1), _Model(a=2)]
        assert _dump_pydantic_model(model) == [{"a": 1}, {"a": 2}]

    def test_dict_of_models(self) -> None:
        model = {"a": _Model(a=1), "b": _Model(a=2)}
        assert _dump_pydantic_model(model) == {"a": {"a": 1}, "b": {"a": 2}}

    def test_str(self):
        assert _dump_pydantic_model("hello") == "hello"

    def test_dict(self):
        assert _dump_pydantic_model({"a": {"a": 1}, "b": {"a": 2}}) == {"a": {"a": 1}, "b": {"a": 2}}


@patch("core.utils.models.dumps._dump_pydantic_model")
def test_safe_dump_pydantic_model(patched_dump_pydantic_model: Mock) -> None:
    patched_dump_pydantic_model.side_effect = ValueError()

    # should not raise
    assert safe_dump_pydantic_model({"bla": "bla"}) is None
