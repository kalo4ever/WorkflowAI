from core.domain.fields.file import File
from core.domain.message import Message


def merge_messages(messages: list[Message], role: Message.Role):
    """
    Merges message content and images from a list of messages

    """

    contents: list[str] = []
    files: list[File] = []

    for message in messages:
        contents.append(message.content)
        if message.files:
            files.extend(message.files)

    return Message(
        content="\n\n".join(contents),
        files=files if files else None,
        role=role,
    )
