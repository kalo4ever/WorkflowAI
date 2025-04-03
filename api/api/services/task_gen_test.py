from api.schemas.build_task_request import BuildAgentIteration, BuildAgentRequest
from api.services.task_gen import get_new_task_input_from_request
from core.agents.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson
from core.domain.fields.chat_message import AssistantChatMessage, UserChatMessage


def test_no_previous_iterations() -> None:
    request = BuildAgentRequest(previous_iterations=[], user_message="user_message_0")

    chat_messages, existing_task = get_new_task_input_from_request(request)

    assert chat_messages == [UserChatMessage(content="user_message_0")]
    assert existing_task is None


def test_with_previous_iterations() -> None:
    request = BuildAgentRequest(
        previous_iterations=[BuildAgentIteration(user_message="user_message_0", assistant_answer="assistant_answer_0")],
        user_message="user_message_1",
    )

    chat_messages, existing_task = get_new_task_input_from_request(request)

    assert chat_messages == [
        UserChatMessage(content="user_message_0"),
        AssistantChatMessage(content="assistant_answer_0"),
        UserChatMessage(content="user_message_1"),
    ]
    assert existing_task is None


def test_with_previous_iterations_and_existing_task() -> None:
    request = BuildAgentRequest(
        previous_iterations=[
            BuildAgentIteration(
                user_message="user_message_0",
                assistant_answer="assistant_answer_0",
                task_schema=BuildAgentIteration.AgentSchema(
                    task_name="task_name_0",
                    input_json_schema={"type": "object"},
                    output_json_schema={"type2": "object"},
                ),
            ),
        ],
        user_message="user_message_1",
    )

    chat_messages, existing_task = get_new_task_input_from_request(request)

    assert chat_messages == [
        UserChatMessage(content="user_message_0"),
        AssistantChatMessage(content="assistant_answer_0"),
        UserChatMessage(content="user_message_1"),
    ]
    assert existing_task == AgentSchemaJson(
        agent_name="task_name_0",
        input_json_schema={"type": "object"},
        output_json_schema={"type2": "object"},
    )


def test_with_previous_iterations_and_existing_task_2() -> None:
    request = BuildAgentRequest(
        previous_iterations=[
            BuildAgentIteration(
                user_message="user_message_0",
                assistant_answer="assistant_answer_0",
                task_schema=BuildAgentIteration.AgentSchema(
                    task_name="task_name_0",
                    input_json_schema={"type": "object"},
                    output_json_schema={"type2": "object"},
                ),
            ),
            BuildAgentIteration(user_message="user_message_1", assistant_answer="assistant_answer_1"),
        ],
        user_message="user_message_2",
    )

    chat_messages, existing_task = get_new_task_input_from_request(request)

    assert chat_messages == [
        UserChatMessage(content="user_message_0"),
        AssistantChatMessage(content="assistant_answer_0"),
        UserChatMessage(content="user_message_1"),
        AssistantChatMessage(content="assistant_answer_1"),
        UserChatMessage(content="user_message_2"),
    ]
    assert existing_task == AgentSchemaJson(
        agent_name="task_name_0",
        input_json_schema={"type": "object"},
        output_json_schema={"type2": "object"},
    )
