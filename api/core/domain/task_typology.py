from typing import Any, cast

from pydantic import BaseModel, Field

from core.domain.fields.file import FileKind
from core.utils.schema_sanitation import get_file_format
from core.utils.schemas import JsonSchema


class TaskTypology(BaseModel):
    has_image_in_input: bool = Field(default=False, description="Whether the task is a 'vision' task")
    has_multiple_images_in_input: bool = Field(
        default=False,
        description="Whether the task support multiple images in inputs",
    )
    has_audio_in_input: bool = Field(default=False, description="Whether the task support audio in inputs")
    has_pdf_in_input: bool = Field(default=False, description="Whether the task support pdf in inputs")

    def _assign_from_schema(self, schema: JsonSchema, is_array: bool):
        followed: str | None = schema.get("$ref")
        if followed is None:
            is_array = schema.type == "array"
            for _, child in schema.child_iterator(follow_refs=False):
                self._assign_from_schema(child, is_array)
            return

        format = get_file_format(followed, cast(dict[str, Any], schema.schema))

        match format:
            case FileKind.IMAGE:
                if is_array or self.has_image_in_input:
                    self.has_multiple_images_in_input = True
                self.has_image_in_input = True
            case FileKind.AUDIO:
                self.has_audio_in_input = True
            case FileKind.PDF:
                self.has_pdf_in_input = True
            case _:
                pass

    @classmethod
    def from_schema(cls, schema: dict[str, Any]):
        raw = TaskTypology()
        # No defs, so typology is empty
        if not schema.get("$defs"):
            return raw

        raw._assign_from_schema(JsonSchema(schema), False)

        return raw

    def __str__(self):
        typology_desc: list[str] = []
        if self.has_image_in_input:
            typology_desc.append("image input")
            if self.has_multiple_images_in_input:
                typology_desc.append("multiple images")
        if self.has_audio_in_input:
            typology_desc.append("audio input")
        if not typology_desc:
            typology_desc.append("text only")
        return " + ".join(typology_desc)
