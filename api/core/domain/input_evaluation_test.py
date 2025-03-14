import pytest

from core.domain.input_evaluation import InputEvaluation


@pytest.fixture()
def input_evaluation() -> InputEvaluation:
    return InputEvaluation(task_input_hash="", correct_outputs=[], incorrect_outputs=[])


class TestAddOutput:
    def test_add_output(self, input_evaluation: InputEvaluation):
        assert input_evaluation.add_output({"a": 1}, True)
        assert input_evaluation.correct_outputs == [{"a": 1}]
        assert input_evaluation.incorrect_outputs == []

    def test_add_output_incorrect(self, input_evaluation: InputEvaluation):
        assert input_evaluation.add_output({"a": 1}, False)
        assert input_evaluation.correct_outputs == []
        assert input_evaluation.incorrect_outputs == [{"a": 1}]

    def test_add_output_already_exists(self, input_evaluation: InputEvaluation):
        input_evaluation.correct_outputs = [{"a": 1}]
        assert not input_evaluation.add_output({"a": 1}, True)

    def test_add_output_already_exists_incorrect(self, input_evaluation: InputEvaluation):
        input_evaluation.incorrect_outputs = [{"a": 1}]
        assert not input_evaluation.add_output({"a": 1}, False)

    def test_remove_from_incorrect_outputs(self, input_evaluation: InputEvaluation):
        input_evaluation.incorrect_outputs = [{"a": 1}]
        assert input_evaluation.add_output({"a": 1}, True)
        assert input_evaluation.correct_outputs == [{"a": 1}]
        assert input_evaluation.incorrect_outputs == []
