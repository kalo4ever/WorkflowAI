import pytest

from api.schemas.evaluators import FaithfulnessEvaluatorBuilder
from core.utils.schemas import JsonSchema
from tests.utils import fixtures_json


class TestFaithfulnessEvaluator:
    def test_find_new_user_message_keypath(self):
        schema_4 = JsonSchema(fixtures_json("jsonschemas", "schema_4.json"))

        keypath = FaithfulnessEvaluatorBuilder.find_new_user_message_keypath(schema_4)
        assert keypath == ["conversation", -1, "content_text"]

    def test_find_new_assistant_answer_keypath(self):
        schema_4 = JsonSchema(
            {
                "properties": {"answer": {"title": "Answer", "type": "string"}},
                "required": ["answer"],
                "title": "ResponsePolicyTaskOutput",
                "type": "object",
            },
        )

        keypath = FaithfulnessEvaluatorBuilder.find_new_assistant_answer_keypath(schema_4)
        assert keypath == ["answer"]

    def test_not_found_keypath(self):
        schema_4 = JsonSchema(
            {
                "properties": {"bla": {"title": "Answer", "type": "string"}},
                "required": ["bla"],
                "title": "ResponsePolicyTaskOutput",
                "type": "object",
            },
        )

        with pytest.raises(ValueError) as e:
            FaithfulnessEvaluatorBuilder.find_new_user_message_keypath(schema_4)

        assert str(e.value) == "Could not find a suitable keypath for new user message"
