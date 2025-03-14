from core.domain.fields.internal_reasoning_steps import InternalReasoningStep


class TestInternalReasoningStepAppendExplanation:
    def test_append_explanation(self):
        step = InternalReasoningStep(explaination=None)
        step.append_explanation("Hello")
        assert step.explaination == "Hello"
        step.append_explanation("World")
        assert step.explaination == "HelloWorld"

    def test_append_explanation_with_existing_explanation(self):
        step = InternalReasoningStep(explaination="Hello")
        step.append_explanation("World")
        assert step.explaination == "HelloWorld"
