import pytest

from core.utils.templates import InvalidTemplateError, TemplateManager


@pytest.fixture
def template_manager():
    return TemplateManager()


class TestCompileTemplate:
    async def test_compile_template(self, template_manager: TemplateManager):
        compiled, variables = await template_manager.compile_template("Hello, {{ name }}!")
        assert compiled
        assert variables == {"name"}

    async def test_compile_complex_template(self, template_manager: TemplateManager):
        template = """
Team Members:
{% for member in team.members %}
- {{ member.name }} ({{ member.role }})
    Projects:
    {% for project in member.projects %}
    * {{ project.name }} - Status: {{ project.status }}
    {% endfor %}
{% endfor %}

{% for project in projects %}
* {{ project.name }} - Status: {{ project.status }}
{% endfor %}

{% if customer.name == "John" %}
Hello, John!
{% else %}
Hello, {{ customer.name }}!
{% endif %}
"""
        compiled, variables = await template_manager.compile_template(template)
        assert compiled
        assert variables == {"team", "projects", "customer"}

    async def test_error_on_missing_variable(self, template_manager: TemplateManager):
        with pytest.raises(InvalidTemplateError) as e:
            await template_manager.compile_template("Hello, {{ name }!")
        assert e.value.message == "unexpected '}'"
        assert e.value.line_number == 1


class TestRenderTemplate:
    async def test_render_template(self, template_manager: TemplateManager):
        data = {"name": "John"}
        rendered, variables = await template_manager.render_template("Hello, {{ name }}!", data)
        assert rendered == "Hello, John!"
        assert variables == {"name"}
        assert data == {"name": "John"}

    async def test_render_template_remaining(self, template_manager: TemplateManager):
        data = {"name": "John", "hello": "world"}
        rendered, variables = await template_manager.render_template(
            "Hello, {{ name }}!",
            data,
        )
        assert rendered == "Hello, John!"
        assert variables == {"name"}
        assert data == {"name": "John", "hello": "world"}
