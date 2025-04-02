from core.agents.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson


def test_agent_schema_json_serialization():
    assert AgentSchemaJson(
        agent_name="Translate Word",
        input_json_schema={},
        output_json_schema={},
    ).model_dump() == {
        "agent_name": "Translate Word",
        "input_json_schema": {},
        "output_json_schema": {},
    }
