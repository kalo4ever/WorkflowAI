import hashlib

import pytest

from core.runners.workflowai.templates import (
    DEPRECATED_TEMPLATES,
    TEMPLATES,
    TemplateName,
    get_template_content,
    sanitize_template_name,
)


@pytest.mark.parametrize(
    "template_name,hash1,hash2",
    [
        # (TemplateName.V1, "332bda8e7399cc12db72a4414f07acea", "53d3526b70c88a51137e7b46413a4931"),
        # (TemplateName.NO_OUTPUT_SCHEMA, "3da61cb39b21d1a675710d3ecd65d3ed", "53d3526b70c88a51137e7b46413a4931"),
        # (
        #     TemplateName.WITH_TOOL_USE_AND_NO_OUTPUT_SCHEMA,
        #     "b60b0cfc53022835157ba1d138a6f9a5",
        #     "53d3526b70c88a51137e7b46413a4931",
        # ),
        # (TemplateName.WITH_TOOL_USE, "4208541189a89d918737e278161b7319", "53d3526b70c88a51137e7b46413a4931"),
        (TemplateName.V2_DEFAULT, "26796376c66436d5f88b5a6f09d7b6d7", "d90035d5906e4f634dffbfc77a5298a0"),
        # (TemplateName.V2_TOOL_USE, "cff7db0da3ac80c4e75de3f7099af926", "d90035d5906e4f634dffbfc77a5298a0"),
        # (
        #     TemplateName.V2_STRUCTURED_GENERATION_AND_TOOL_USE,
        #     "e41ee9f9e04ca34c971ebd6be024b4f3",
        #     "d90035d5906e4f634dffbfc77a5298a0",
        # ),
        (TemplateName.V2_STRUCTURED_GENERATION, "b317f97d411e42d247b9d78248d4d922", "d90035d5906e4f634dffbfc77a5298a0"),
        (
            TemplateName.V2_DEFAULT_NO_INPUT_SCHEMA,
            "36090376b06f21c654a5993a35d951d1",
            "d90035d5906e4f634dffbfc77a5298a0",
        ),
        (
            TemplateName.V2_STRUCTURED_GENERATION_NO_INPUT_SCHEMA,
            "35af1c2c39f294cca543548f755042fc",
            "d90035d5906e4f634dffbfc77a5298a0",
        ),
        # (
        #     TemplateName.V2_TOOL_USE_NO_INPUT_SCHEMA,
        #     "56a5703d1f9a72d9770dc8a9f150969c",
        #     "d90035d5906e4f634dffbfc77a5298a0",
        # ),
        # (
        #     TemplateName.V2_STRUCTURED_GENERATION_AND_TOOL_USE_NO_INPUT_SCHEMA,
        #     "abe2617e0f30a9c638f2f7032835d547",
        #     "d90035d5906e4f634dffbfc77a5298a0",
        # ),
    ],
)
def test_template_hashes(template_name: TemplateName, hash1: str, hash2: str):
    # Templates should not be modified. So the hashes should never change.
    t1, t2 = TEMPLATES[template_name]

    assert hashlib.md5(t1.encode()).hexdigest() == hash1
    assert hashlib.md5(t2.encode()).hexdigest() == hash2


def test_get_template_content_V2_DEFAULT_NO_INPUT_SCHEMA():
    # Test that the template content is correct
    system_template, user_template = get_template_content(TemplateName.V2_DEFAULT_NO_INPUT_SCHEMA)
    assert (
        system_template
        == """<instructions>
{{instructions}}
</instructions>

Return a single JSON object enforcing the following schema:
```json
{{output_schema}}
```"""
    )
    assert (
        user_template
        == """Input is:
```json
{{input_data}}
```{{examples}}"""
    )


class TestSanitizeTemplateName:
    @pytest.mark.parametrize(
        "template_name,is_tool_use,is_structured_gen,supports_input_schema,expected",
        [
            # Test deprecated templates get converted
            ("v1", True, True, True, TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE),
            ("v1", True, False, True, TemplateName.V2_NATIVE_TOOL_USE),
            ("v1", False, True, True, TemplateName.V2_STRUCTURED_GENERATION),
            ("no_output_schema", False, False, True, TemplateName.V2_DEFAULT),
            # Test new template names are preserved
            (TemplateName.V2_DEFAULT.value, True, True, True, TemplateName.V2_DEFAULT),
            (TemplateName.V2_TOOL_USE.value, True, False, True, TemplateName.V2_NATIVE_TOOL_USE),
            (
                TemplateName.V2_STRUCTURED_GENERATION.value,
                False,
                True,
                True,
                TemplateName.V2_STRUCTURED_GENERATION,
            ),
            (
                TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE.value,
                True,
                True,
                True,
                TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE,
            ),
            # Test None template name uses default logic
            (None, True, True, True, TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE),
            (None, True, False, True, TemplateName.V2_NATIVE_TOOL_USE),
            (None, False, True, True, TemplateName.V2_STRUCTURED_GENERATION),
            (None, False, False, True, TemplateName.V2_DEFAULT),
            # Test invalid template name falls back to default
            ("invalid_template", True, True, True, TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE),
            ("not_real", False, False, True, TemplateName.V2_DEFAULT),
            # Test model that does not support input schema
            (
                None,
                True,
                True,
                False,
                TemplateName.V2_STRUCTURED_GENERATION_AND_NATIVE_TOOL_USE_NO_INPUT_SCHEMA,
            ),
            (None, True, False, False, TemplateName.V2_NATIVE_TOOL_USE_NO_INPUT_SCHEMA),
            (
                None,
                False,
                True,
                False,
                TemplateName.V2_STRUCTURED_GENERATION_NO_INPUT_SCHEMA,
            ),
            (None, False, False, False, TemplateName.V2_DEFAULT_NO_INPUT_SCHEMA),
        ],
    )
    def test_sanitize_template_name(
        self,
        template_name: str | None,
        is_tool_use: bool,
        is_structured_gen: bool,
        supports_input_schema: bool,
        expected: TemplateName,
    ):
        result = sanitize_template_name(
            template_name=template_name,
            is_tool_use_enabled=is_tool_use,
            is_structured_generation_enabled=is_structured_gen,
            supports_input_schema=supports_input_schema,
        )
        assert result not in DEPRECATED_TEMPLATES
        assert result == expected


class TestDeprecatedTemplates:
    def test_exhaustive(self):
        """Check that either a template is deprecated or has a config"""
        final_templates = sorted([*DEPRECATED_TEMPLATES, *TEMPLATES.keys()])
        assert final_templates == sorted(list(TemplateName))
