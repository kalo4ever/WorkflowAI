from copy import deepcopy
from enum import Enum
from typing import Any

import pytest
from pydantic import BaseModel, Field

from tests.models import task_variant

from .python_gen import (
    RunTemplateArgs,
    _fn_name,  # pyright: ignore [reportPrivateUsage]
    _input_str,  # pyright: ignore [reportPrivateUsage]
    _prints,  # pyright: ignore [reportPrivateUsage]
    _run_code_block,  # pyright: ignore [reportPrivateUsage]
    _run_template,  # pyright: ignore [reportPrivateUsage]
    _stream_code_block,  # pyright: ignore [reportPrivateUsage]
    generate_full_run_code,
)


class CityCurrencyExtractionInput(BaseModel):
    city: str = Field(
        ...,
        description="The name of the city for which the currency needs to be extracted",
        examples=["Paris"],
    )

    class Currency(Enum):
        USD = "USD"
        EUR = "EUR"
        JPY = "JPY"
        GBP = "GBP"
        AUD = "AUD"
        CAD = "CAD"
        CHF = "CHF"
        CNY = "CNY"
        SEK = "SEK"
        NZD = "NZD"
        AED = "AED"
        OTHER = "OTHER"

    currency: Currency = Field(
        ...,
        description="The currency in which the prices are displayed",
    )


class TestPrint:
    def test_prints(self):
        assert (
            _prints("run")
            == """
    print("\\n--------\\nOutput:\\n", run.output, "\\n--------\\n")
    print("Model: ", run.version.properties.model)
    print("Cost: $", run.cost_usd)
    print(f"Latency: {run.duration_seconds:.2f}s")"""
        )


class TestRunTemplate:
    kwargs = RunTemplateArgs(
        fn_name="email_conversation",
        input_name="EmailConversationInput",
        output_name="EmailConversationOutput",
        task_id="email-conversation",
        schema_id=1,
        version="production",
    )

    def test_run_full(self):
        assert (
            _run_template(**self.kwargs)
            == """@workflowai.agent(schema_id=1, version="production")
async def email_conversation(_: EmailConversationInput) -> EmailConversationOutput:
    # Leave the function body empty
    ..."""
        )

    def test_run_full_different_id(self):
        kwargs: RunTemplateArgs = {**self.kwargs, "task_id": "123"}
        assert (
            _run_template(**kwargs)
            == """@workflowai.agent(id="123", schema_id=1, version="production")
async def email_conversation(_: EmailConversationInput) -> EmailConversationOutput:
    # Leave the function body empty
    ..."""
        )

    def test_run_full_int_version(self):
        kwargs: RunTemplateArgs = {**self.kwargs, "version": 1}
        assert (
            _run_template(**kwargs)
            == """@workflowai.agent(schema_id=1, version=1)
async def email_conversation(_: EmailConversationInput) -> EmailConversationOutput:
    # Leave the function body empty
    ..."""
        )


@pytest.fixture
def email_conversation_input_schema():
    return {
        "type": "object",
        "properties": {
            "email_conversation": {
                "description": "An array of email messages in the conversation",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sender": {"description": "The email address of the sender", "type": "string"},
                        "recipient": {"description": "The email address of the recipient", "type": "string"},
                        "subject": {"description": "The subject line of the email", "type": "string"},
                        "body": {"description": "The main content of the email", "type": "string"},
                        "timestamp": {
                            "title": "DatetimeLocal",
                            "type": "object",
                            "properties": {
                                "date": {"title": "Date", "type": "string", "format": "date"},
                                "local_time": {"title": "Local Time", "type": "string", "format": "time"},
                                "timezone": {"title": "Timezone", "type": "string", "format": "timezone"},
                            },
                        },
                    },
                },
            },
        },
        "title": "EmailConversation",
    }


@pytest.fixture
def email_conversation_example_input():
    return {
        "email_conversation": [
            {
                "sender": "spatika@workflowai.com",
                "recipient": "spatika@workflowai.com",
                "subject": "TestingFeature",
                "body": "This is a feature testing and of okayish importance.",
                "timestamp": {
                    "date": "2024-09-12",
                    "local_time": "12:05:00",
                    "timezone": "America/New_York",
                },
            },
        ],
    }


class TestInputStr:
    def test_no_secondary_input(
        self,
        email_conversation_input_schema: dict[str, Any],
        email_conversation_example_input: dict[str, Any],
    ):
        out = _input_str(
            name="EmailConversationInput",
            input_schema=email_conversation_input_schema,
            example_input=email_conversation_example_input,
            secondary_input=None,
            model_classes=[],
        )
        assert (
            out
            == """
    agent_input = EmailConversationInput(
        email_conversation=[
            EmailConversation(
                sender='spatika@workflowai.com',
                recipient='spatika@workflowai.com',
                subject='TestingFeature',
                body='This is a feature testing and of okayish importance.',
                timestamp=DatetimeLocal(
                    date='2024-09-12',
                    local_time='12:05:00',
                    timezone='America/New_York',
                ),
            ),
        ],
    )""".strip("\n")
        )

    def test_secondary_input(
        self,
        email_conversation_input_schema: dict[str, Any],
        email_conversation_example_input: dict[str, Any],
    ):
        sec = deepcopy(email_conversation_example_input)
        sec["email_conversation"][0]["sender"] = "other@workflowai.com"

        out = _input_str(
            name="EmailConversationInput",
            input_schema=email_conversation_input_schema,
            example_input=email_conversation_example_input,
            secondary_input=sec,
            model_classes=[],
        )
        assert (
            out
            == """
    agent_input = EmailConversationInput(
        email_conversation=[
            EmailConversation(
                sender='spatika@workflowai.com',
                recipient='spatika@workflowai.com',
                subject='TestingFeature',
                body='This is a feature testing and of okayish importance.',
                timestamp=DatetimeLocal(
                    date='2024-09-12',
                    local_time='12:05:00',
                    timezone='America/New_York',
                ),
            ),
        ],
    )
    # agent_input = EmailConversationInput(
    #     email_conversation=[
    #         EmailConversation(
    #             sender='other@workflowai.com',
    #             recipient='spatika@workflowai.com',
    #             subject='TestingFeature',
    #             body='This is a feature testing and of okayish importance.',
    #             timestamp=DatetimeLocal(
    #                 date='2024-09-12',
    #                 local_time='12:05:00',
    #                 timezone='America/New_York',
    #             ),
    #         ),
    #     ],
    # )""".strip("\n")
        )


class TestRunCodeBlock:
    kwargs = RunTemplateArgs(
        fn_name="email_conversation",
        input_name="EmailConversationInput",
        output_name="EmailConversationOutput",
        task_id="email-conversation",
        schema_id=1,
        version="production",
    )

    def test_run_code_block(self):
        code = _run_code_block("blabla", **self.kwargs)
        assert (
            code
            == """@workflowai.agent(schema_id=1, version="production")
async def email_conversation(_: EmailConversationInput) -> EmailConversationOutput:
    # Leave the function body empty
    ...

async def run_with_example():
blabla
    try:
        # Cache options:
        # - "auto" (default): returns a cached output only if all conditions are met:
        #   1. A previous run exists with matching version and input
        #   2. Temperature is set to 0
        #   3. No tools are enabled
        # - "always": a cached output is returned when available, regardless
        # of the temperature value or enabled tools
        # - "never": the cache is never used
        run = await email_conversation.run(agent_input, use_cache="auto")
    except WorkflowAIError as e:
        print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")
        return

    print("\\n--------\\nOutput:\\n", run.output, "\\n--------\\n")
    print("Model: ", run.version.properties.model)
    print("Cost: $", run.cost_usd)
    print(f"Latency: {run.duration_seconds:.2f}s")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""
        )


class TestStreamCodeBlock:
    kwargs = RunTemplateArgs(
        fn_name="email_conversation",
        input_name="EmailConversationInput",
        output_name="EmailConversationOutput",
        task_id="email-conversation",
        schema_id=1,
        version="production",
    )

    def test_stream_code_block(self):
        code = _stream_code_block("blabla", **self.kwargs)
        assert (
            code
            == """@workflowai.agent(schema_id=1, version="production")
async def email_conversation(_: EmailConversationInput) -> EmailConversationOutput:
    # Leave the function body empty
    ...

async def run_with_example():
blabla
    try:
        # Cache options:
        # - "auto" (default): returns a cached output only if all conditions are met:
        #   1. A previous run exists with matching version and input
        #   2. Temperature is set to 0
        #   3. No tools are enabled
        # - "always": a cached output is returned when available, regardless
        # of the temperature value or enabled tools
        # - "never": the cache is never used
        async for chunk in email_conversation.stream(agent_input, use_cache="auto"):
            # All intermediate chunks contains a partial output
            print(chunk)
    except WorkflowAIError as e:
        print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")
        return

    # The last chunk contains the final validated output and additional run information
    print("\\n--------\\nOutput:\\n", chunk.output, "\\n--------\\n")
    print("Model: ", chunk.version.properties.model)
    print("Cost: $", chunk.cost_usd)
    print(f"Latency: {chunk.duration_seconds:.2f}s")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""
        )


class TestGenerateFullRunCode:
    def test_generate_full_run_code(self):
        variant = task_variant()
        example_input = {"input": "test"}

        code = generate_full_run_code(variant, example_input, version="production")

        assert (
            code.common
            == """# Initialize the shared client
# Not required if the api key is defined using the WORKFLOWAI_API_KEY environment variable
# workflowai.init(api_key=os.environ["WORKFLOWAI_API_KEY"])


class TaskNameInput(BaseModel):
    input: str

class TaskNameOutput(BaseModel):
    output: int"""
        )

        assert (
            code.run.imports
            == """from pydantic import BaseModel
import workflowai
from workflowai import Run, WorkflowAIError"""
        )

        assert (
            code.run.code
            == """@workflowai.agent(id="task_id", schema_id=1, version="production")
async def task_name(_: TaskNameInput) -> TaskNameOutput:
    # Leave the function body empty
    ...

async def run_with_example():
    agent_input = TaskNameInput(
        input=\'test\',
    )
    try:
        # Cache options:
        # - "auto" (default): returns a cached output only if all conditions are met:
        #   1. A previous run exists with matching version and input
        #   2. Temperature is set to 0
        #   3. No tools are enabled
        # - "always": a cached output is returned when available, regardless
        # of the temperature value or enabled tools
        # - "never": the cache is never used
        run = await task_name.run(agent_input, use_cache="auto")
    except WorkflowAIError as e:
        print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")
        return

    print("\\n--------\\nOutput:\\n", run.output, "\\n--------\\n")
    print("Model: ", run.version.properties.model)
    print("Cost: $", run.cost_usd)
    print(f"Latency: {run.duration_seconds:.2f}s")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""
        )

        assert (
            code.stream.imports
            == """from pydantic import BaseModel
import workflowai
from workflowai import Run, WorkflowAIError
from collections.abc import AsyncIterator"""
        )

        assert (
            code.stream.code
            == """@workflowai.agent(id="task_id", schema_id=1, version="production")
async def task_name(_: TaskNameInput) -> TaskNameOutput:
    # Leave the function body empty
    ...

async def run_with_example():
    agent_input = TaskNameInput(
        input=\'test\',
    )
    try:
        # Cache options:
        # - "auto" (default): returns a cached output only if all conditions are met:
        #   1. A previous run exists with matching version and input
        #   2. Temperature is set to 0
        #   3. No tools are enabled
        # - "always": a cached output is returned when available, regardless
        # of the temperature value or enabled tools
        # - "never": the cache is never used
        async for chunk in task_name.stream(agent_input, use_cache="auto"):
            # All intermediate chunks contains a partial output
            print(chunk)
    except WorkflowAIError as e:
        print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")
        return

    # The last chunk contains the final validated output and additional run information
    print("\\n--------\\nOutput:\\n", chunk.output, "\\n--------\\n")
    print("Model: ", chunk.version.properties.model)
    print("Cost: $", chunk.cost_usd)
    print(f"Latency: {chunk.duration_seconds:.2f}s")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""
        )


class TestInputStrWitt:
    def test_with_model_class(self):
        out = _input_str(
            name="CityCurrencyInput",
            input_schema={
                "type": "object",
                "properties": {
                    "options": {
                        "type": "object",
                        "properties": {"currency": {"type": "string", "enum": ["USD", "EUR", "JPY"]}},
                    },
                },
            },
            example_input={"options": {"currency": "EUR"}},
            secondary_input=None,
            model_classes=["CityCurrencyInput", "Option"],
        )
        assert (
            out
            == """
    agent_input = CityCurrencyInput(
        options=Option(
            currency='EUR',
        ),
    )""".strip("\n")
        )


class TestGenerateValidFunctionName:
    def test_basic_name(self):
        assert _fn_name("Hello World") == "hello_world"

    def test_multiple_spaces(self):
        assert _fn_name("Hello   World") == "hello___world"

    def test_numbers(self):
        assert _fn_name("Hello 123 World") == "hello_123_world"

    def test_leading_number(self):
        assert _fn_name("123 Hello") == "hello"

    def test_empty_string(self):
        assert _fn_name("") == "func"

    def test_leading_number_task_name(self):
        assert _fn_name("123HelloWorld") == "hello_world"
