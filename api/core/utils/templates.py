import asyncio
import re
from typing import Any

from cachetools import LRUCache
from jinja2 import Environment, Template, TemplateError
from jinja2.meta import find_undeclared_variables

# Compiled regepx to check if instructions are a template
# Jinja templates use  {%%} for expressions {{}} for variables and {# ... #} for comments

_template_regex = re.compile(rf"({re.escape("{%")}|{re.escape("{{")}|{re.escape("{#")})")


class InvalidTemplateError(Exception):
    def __init__(self, message: str, lineno: int | None):
        self.message = message
        self.line_number = lineno

    def __str__(self) -> str:
        return f"{self.message} (line {self.line_number})"

    @classmethod
    def from_jinja(cls, e: TemplateError):
        return cls(e.message or str(e), getattr(e, "lineno", None))


class TemplateManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._template_cache = LRUCache[int, tuple[Template, set[str]]](maxsize=10)
        self._template_env = Environment(enable_async=True)

    def _key(self, template: str) -> int:
        return hash(template)

    @classmethod
    def is_template(cls, template: str) -> bool:
        return bool(_template_regex.search(template))

    @classmethod
    async def compile_template(cls, template: str) -> tuple[Template, set[str]]:
        try:
            env = Environment(enable_async=True)
            source = env.parse(source=template)
            variables = find_undeclared_variables(source)
            compiled = env.from_string(source=template)
            return compiled, variables
        except TemplateError as e:
            raise InvalidTemplateError.from_jinja(e)

    async def add_template(self, template: str) -> tuple[Template, set[str]]:
        async with self._lock:
            try:
                return self._template_cache[self._key(template)]
            except KeyError:
                pass

        compiled = await self.compile_template(template)
        async with self._lock:
            self._template_cache[self._key(template)] = compiled
        return compiled

    async def render_template(self, template: str, data: dict[str, Any]):
        """Render the template. Returns the variables that were used in the template"""
        compiled, variables = await self.add_template(template)

        rendered = await compiled.render_async(data)
        return rendered, variables
