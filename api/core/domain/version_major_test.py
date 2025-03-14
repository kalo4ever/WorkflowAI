from core.domain.models import Model
from core.domain.version_major import VersionMajor


class TestMinorProperties:
    def test_validate_model_str(self):
        validated = VersionMajor.Minor.Properties.model_validate({"model": "gpt-4o", "temperature": 0.0})
        assert validated.model == "gpt-4o"
        assert validated.temperature == 0.0

    def test_validate_model(self):
        validated = VersionMajor.Minor.Properties.model_validate(
            {"model": Model.GPT_4O_LATEST.value, "temperature": 0.0},
        )
        assert isinstance(validated.model, Model)
        assert validated.model == Model.GPT_4O_LATEST
        assert validated.temperature == 0.0
