import json
from typing import Any, List, Optional

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model

from core.domain.task_variant import SerializableTaskVariant


class Properties(BaseModel):
    temperature: Optional[float] = None
    instructions: Optional[str] = None
    few_shot: Optional[bool] = None


class Schema(BaseModel):
    input_json_schema: Optional[str] = None
    output_json_schema: Optional[str] = None

    @classmethod
    def from_task_variant(cls, task_variant: SerializableTaskVariant):
        return cls(
            input_json_schema=json.dumps(task_variant.input_schema.json_schema),
            output_json_schema=json.dumps(task_variant.output_schema.json_schema),
        )


class TaskGroupWithSchema(BaseModel):
    properties: Optional[Properties] = None
    schema_: Optional[Schema] = Field(None, alias="schema")


class GenerateChangelogFromPropertiesTaskInput(BaseModel):
    old_task_group: TaskGroupWithSchema | None = None
    new_task_group: TaskGroupWithSchema | None = None

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        kwargs = {"by_alias": True, **kwargs}
        return super().model_dump(*args, **kwargs)


class GenerateChangelogFromPropertiesTaskOutput(BaseModel):
    changes: Optional[List[str]] = None


@workflowai.agent(id="generate-changelog-from-properties", model=Model.GEMINI_1_5_PRO_002)
async def generate_changelog_from_properties(
    input: GenerateChangelogFromPropertiesTaskInput,
) -> GenerateChangelogFromPropertiesTaskOutput:
    """Compare the properties from old_task_group with new_task_group, then describe the changes made.

    Focus on identifying additions, removals, or modifications in the wording or requirements.

    Present the changes in a concise, bullet-point format, directly describing the changes without mentioning property names like 'Instructions modified.'.

    Order the changes so that modifications to 'instructions' are listed first, followed by changes to 'temperature', 'few_shot', and any other properties.

    Be specific about what has been altered or emphasized in the current instruction compared to the previous one.

    When mentioning temperature changes, use the specific names (Precise, Balanced, Creative) instead of the numeric values.

    Some temperature values have 3 specific names:
    - when exactly 0, Precise
    - when exactly 0.5, Balanced
    - when exactly 1, Creative

    Example:
    Added a note about...
    Temperature increased from Precise to Balanced.
    Temperature increased from Precise to 1.2.
    Temperature decreased from 0.9 to Balanced."""
    ...
