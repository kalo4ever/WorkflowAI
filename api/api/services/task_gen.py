from typing import Optional

from api.schemas.build_task_request import BuildAgentRequest
from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson
from core.domain.fields.chat_message import AssistantChatMessage, ChatMessage, UserChatMessage
from core.utils.iter_utils import last_where


def get_new_task_input_from_request(request: BuildAgentRequest) -> tuple[list[ChatMessage], Optional[AgentSchemaJson]]:
    chat_messages: list[ChatMessage] = []
    existing_task: Optional[AgentSchemaJson] = None

    # Build the chat messages from the previous iteration request
    for iteration in request.previous_iterations or []:
        chat_messages.append(UserChatMessage(content=iteration.user_message))
        chat_messages.append(AssistantChatMessage(content=iteration.assistant_answer))

    # Add the latest user message from the request
    chat_messages.append(UserChatMessage(content=request.user_message))

    # Build the existing task from the request
    if request.previous_iterations and len(request.previous_iterations) > 0:
        latest_iteration_with_schema = last_where(
            request.previous_iterations,
            lambda i: i.task_schema is not None,
        )

        if (
            latest_iteration_with_schema
            and latest_iteration_with_schema.task_schema  # for type checking only, since we already checked this in 'last_where'
            is not None
        ):
            existing_task = AgentSchemaJson(
                agent_name=latest_iteration_with_schema.task_schema.task_name,
                input_json_schema=latest_iteration_with_schema.task_schema.input_json_schema,
                output_json_schema=latest_iteration_with_schema.task_schema.output_json_schema,
            )

    return chat_messages, existing_task
