from api.schemas.version_properties import FullVersionProperties, ShortVersionProperties
from core.domain.task_group_properties import TaskGroupProperties


class TestShortVersionProperties:
    def test_model_name_and_icon_on_not_found(self):
        """Test with a model that is not found in the MODEL_DATAS"""
        properties = ShortVersionProperties(model="gpt-4o")
        assert properties.model_name is None
        assert properties.model_icon is None

    def test_model_name_and_icon_on_found(self):
        """Test with a model that is found in the MODEL_DATAS"""
        properties = ShortVersionProperties(model="gpt-4o-latest")
        assert properties.model_name
        assert properties.model_icon


class TestFullVersionProperties:
    def test_model_name_and_icon_on_not_found(self):
        """Test with a model that is not found in the MODEL_DATAS"""
        properties = FullVersionProperties(model="gpt-4o")
        assert properties.model_name is None
        assert properties.model_icon is None

    def test_from_domain(self):
        """Test that the from_domain method works"""
        properties = FullVersionProperties.from_domain(TaskGroupProperties(model="gpt-4o-latest"))
        assert properties.model == "gpt-4o-latest"
        assert properties.model_name
        assert properties.model_icon
