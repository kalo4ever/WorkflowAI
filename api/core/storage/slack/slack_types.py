from typing import Literal, NotRequired, TypedDict


class SlackTextBlock(TypedDict):
    type: Literal["mrkdwn"]
    text: str


class SlackPlainTextBlock(TypedDict):
    type: Literal["plain_text"]
    text: str
    emoji: NotRequired[bool]


class SlackImageAccessory(TypedDict):
    type: Literal["image"]
    image_url: str
    alt_text: NotRequired[str]


class SlackHeaderBlock(TypedDict):
    type: Literal["header"]
    text: SlackPlainTextBlock


class SlackButtonElement(TypedDict):
    type: Literal["button"]
    text: SlackPlainTextBlock
    style: NotRequired[Literal["primary", "danger"]]
    value: str
    url: NotRequired[str]


class SlackActionsBlock(TypedDict):
    type: Literal["actions"]
    elements: list[SlackButtonElement]


class SlackSectionBlock(TypedDict, total=False):
    type: Literal["section"]
    text: NotRequired[SlackTextBlock]
    block_id: NotRequired[str]
    accessory: NotRequired[SlackImageAccessory]
    fields: NotRequired[list[SlackTextBlock]]


SlackBlock = SlackSectionBlock | SlackHeaderBlock | SlackActionsBlock


class SlackMessage(TypedDict):
    text: NotRequired[str]
    blocks: NotRequired[list[SlackBlock]]
