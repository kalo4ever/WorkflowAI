import workflowai
from pydantic import BaseModel, Field

from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import (
    InputObjectFieldConfig,
    OutputObjectFieldConfig,
)


class SchemaBuilderInput(BaseModel):
    agent_name: str = Field(
        description="The name of the new agent we are generating the schema for",
    )
    agent_description: str | None = Field(
        default=None,
        description="The description of the new agent we are generating the schema for",
    )
    agent_specifications: str | None = Field(
        default=None,
        description="The specifications of the new agent we are generating the schema for, if any",
    )
    available_tools_description: str | None = Field(
        default=None,
        description="The description of the available tools, potentially available for the agent we are generating the schema for",
    )
    company_context: str | None = Field(
        default=None,
        description="The context of the user's company, to inform the decision about the new agents schema",
    )


class NewAgentSchema(BaseModel):
    input_schema: InputObjectFieldConfig | None = Field(description="The schema of the agent input", default=None)
    output_schema: OutputObjectFieldConfig | None = Field(description="The schema of the agent output", default=None)


class SchemaBuilderOutput(BaseModel):
    new_agent_schema: NewAgentSchema | None = Field(
        description="The new agent schema, if any, after processing of the 'new_message'",
        default=None,
    )


# TODO: switch back to Claude 3.7 when we'll have more token quotas
@workflowai.agent(id="agent-schema-generation", model=workflowai.Model.CLAUDE_3_5_HAIKU_20241022)
async def run_agent_schema_generation(
    input: SchemaBuilderInput,
) -> SchemaBuilderOutput:
    """You are an expert in generating schemas for AI agents, based on agents name, description and (optionally) specifications.

    You have to define input and output objects for an agent that will be given to an LLM.
    Assume that the LLM will not be able to retrieve any context and that the input should contain all the necessary information for the agent.


    What to include in the schema?
    - Do not extrapolate user's instructions and create too many fields. Always use the minimum fields to perform the agent goal described by the user. Better to start with a simple schema and refine, than the opposite.
    - Do not add extra fields that are not asked by the user.
    - Use 'enum' field type in the 'input_schema' IF AND ONLY IF the user EXPLICITLY requests to use 'enums" (ex: "this field should be an enum"), if the word "enum" is absent from the user's message, you CAN NOT use enums in the input schema. Prefer using 'string', even for fields that can have a predefined, limited set of values. Example. Note that those restrictions do not apply to 'output_schema' where the use of enums is encouraged, when that makes sense.
    - Do not add an 'explanation' field in the 'output_schema' unless asked by the user.
    - For classification cases, make sure to include an additional "UNSURE" option, for the cases that are undetermined. Do not use a "confidence_score" unless asked by the user.
    - Make sure to strictly enforce the output schema, even if the user asks otherwise, e.g the 'input_schema' can not contain any examples.
    - When refusing a query, propose an alternative.

    Special considerations for chat-based agents:

    For chat based agent the schema could look like this:
    {
    "agent_name": "Simple Chat",
    "input_schema": {
    "type": "object",
    "fields": [{"name": "messages", "type": "array", "item_type": "object", "fields": [{"name": "role", "type": "enum", "values": ["USER", "ASSISTANT"]}, {"name": "content", "type": "string"}]}]
    },
    "output_schema": {
    "type": "object",
    "fields": [{"name": "assistant_answer", "type": "string"}]
    }
    }

    In case the assistant can return some special messages (ex: weather forecast) the same additional fields MUST be added to the 'messages' field in INPUT (since the chat can be multi-turn) as well as in the OUTPUT schema:
    {
    "agent_name": "Weather Forecast Chat",
    "input_schema": {
    "type": "object",
    "fields": [{"name": "messages", "type": "array", "item_type": "object", "fields": [{"name": "role", "type": "enum", "values": ["USER", "ASSISTANT"]}, {"name": "content", "type": "string"}, {"name": "weather_forecast", "type": "object", "fields": [{"name": "temperature", "type": "number"}, {"name": "condition", "type": "enum", "values": ["sunny", "cloudy", "rainy"]}]}]}]
    },
    "output_schema": {
    "type": "object",
    "fields": [{"name": "assistant_answer", "type": "string"}, {"name": "weather_forecast", "type": "object", "fields": [{"name": "temperature", "type": "number"}, {"name": "condition", "type": "enum", "values": ["sunny", "cloudy", "rainy"]}]}]
    }
    }

    For both chat-based cases, please make sure not to include 'SYSTEM' as a message role.

    Examples:
    - "I want to extract events from an email" -> Input should have an 'email_html' field of type 'html', output should be an array of events (title, start, end, location, description, attendees).
    - "I want to create insights from an article" -> Input should have an 'article' field of type 'string', output should be an array of insights (STRING).
    - "Extract the city and country from the image." -> Input should have an 'image' field of type 'image_file', output should include 'city' and 'country' as strings.
    - "I want to create a chatbot that recommends products to users based on their preferences" -> Input should include 'messages' which is a list of previous conversation turns (each with 'role' and 'content'), output should include the assistant's answer and product recommendations. Ensure the same fields are included in the input schema to account for previous recommendations.
    - "I want to translate texts to Spanish" -> Input must contain a 'text' (string). Output must contain a 'translated_text' (string). Task name: "Text Spanish Translation"

    Schema Generation Rules:

    - The 'new_agent_schema.agent_name' must follow the following convention: [subject that is acted upon] + [the action], in Title Case. Ex: 'Sentiment Analysis', 'Text Summarization', 'Location Detection'. Avoid using "Generation" in the agent name, as all agents perform generation anyway.
    - Enums must always have a 'fallback' value like 'OTHER', 'NA' (when the field does not apply), 'UNSURE' (for classification). This fallback value comes in addition to other values.
    - All fields are optional by default.
    - When an explicit timezone is required for the agent in the output (for example: repeating events at the same time on different days, daylight saving time ambiguities, etc.), you can use the "datetime_local" type that includes date, local_time, and timezone.
    - Image generation, audio generation, and file generation in general, is not supported. Always refer to the InputSchemaFieldType and OutputSchemaFieldType, respectively.
    - 'document_file' allows to support indistinctively text (txt, json, csv, etc), images and pdfs file.
    - If 'available_tools_description' is provided, consider how these tools might be utilized in the agent and adjust the schema accordingly.
    - For cases where the agent requires static or infrequently updated context that does not vary from agent run to agent run, you do not need to include this context in the input schema. Instead, explain in the 'answer_to_user' that the agent instructions are the best place this context. Task instructions are outside of your scope and are generated afterwards by another agent, do not offer to update the instructions. Non-exhaustive examples of large and static content: FAQ knowledge base for customer service agents, Company policies or guidelines for compliance checking agents, Style guides for content creation agents, Standard operating procedures for process analysis agents, reference documentation for technical support agents, etc. As a rule of thumbs, input data that  is supposed to change every time the agent is run can go in the 'input_json_schema', input data that varies way rarely can go in the instructions."""
    ...
