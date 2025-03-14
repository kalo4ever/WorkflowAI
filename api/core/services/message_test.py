from core.domain.fields.file import File
from core.domain.message import Message
from core.services.message import merge_messages


def test_merge_messages_content_only():
    messages = [
        Message(content="Hello", role=Message.Role.USER),
        Message(content="World", role=Message.Role.USER),
    ]
    merged = merge_messages(messages, Message.Role.USER)
    assert merged.content == "Hello\n\nWorld"
    assert merged.files is None
    assert merged.role == Message.Role.USER


def test_merge_messages_with_mixed_files():
    image1 = File(content_type="image/jpeg", data="some data")
    audio1 = File(content_type="audio/wav", data="some other data")
    messages = [
        Message(content="Message 1", files=[image1], role=Message.Role.USER),
        Message(content="Message 2", files=[audio1], role=Message.Role.USER),
    ]
    merged = merge_messages(messages, Message.Role.USER)
    assert merged.content == "Message 1\n\nMessage 2"
    assert merged.files == [image1, audio1]
    assert merged.role == Message.Role.USER


def test_merge_messages_with_images():
    image1 = File(content_type="image/jpeg", data="some data")
    image2 = File(content_type="image/jpeg", data="some other data")
    messages = [
        Message(content="Message 1", files=[image1], role=Message.Role.USER),
        Message(content="Message 2", files=[image2], role=Message.Role.USER),
    ]
    merged = merge_messages(messages, Message.Role.USER)
    assert merged.content == "Message 1\n\nMessage 2"
    assert merged.files == [image1, image2]
    assert merged.role == Message.Role.USER


def test_merge_messages_mixed():
    image = File(content_type="image/jpeg", data="some data")
    audio = File(content_type="audio/wav", data="some data")
    messages = [
        Message(content="Text only", role=Message.Role.USER),
        Message(content="With image", files=[image], role=Message.Role.USER),
        Message(content="With audio", files=[audio], role=Message.Role.USER),
    ]
    merged = merge_messages(messages, Message.Role.USER)
    assert merged.content == "Text only\n\nWith image\n\nWith audio"
    assert merged.files == [image, audio]
    assert merged.role == Message.Role.USER


def test_merge_messages_empty_list():
    merged = merge_messages([], Message.Role.USER)
    assert merged.content == ""
    assert merged.files is None
    assert merged.role == Message.Role.USER


def test_merge_messages_different_roles():
    messages = [
        Message(content="User message", role=Message.Role.USER),
        Message(content="Assistant message", role=Message.Role.ASSISTANT),
    ]
    merged = merge_messages(messages, Message.Role.SYSTEM)
    assert merged.content == "User message\n\nAssistant message"
    assert merged.files is None
    assert merged.role == Message.Role.SYSTEM
