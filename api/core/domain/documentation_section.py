from pydantic import BaseModel, Field


class DocumentationSection(BaseModel):
    title: str = Field(description="The title of the documentation section")
    content: str = Field(description="The content of the documentation section")
