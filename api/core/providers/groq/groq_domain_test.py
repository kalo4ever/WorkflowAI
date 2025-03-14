from core.providers.groq.groq_domain import GroqMessage


class TestMessageToStandard:
    def test_message_to_standard(self) -> None:
        message = GroqMessage(content='{"message": "Hello you"}', role="assistant")
        assert message.to_standard() == {"role": "assistant", "content": '{"message": "Hello you"}'}
