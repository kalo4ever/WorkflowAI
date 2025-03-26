import logging
import os

from api.tasks.meta_agent import MetaAgentChatMessage
from api.tasks.pick_relevant_documentation_categories import (
    PickRelevantDocumentationSectionsInput,
    pick_relevant_documentation_sections,
)
from core.domain.documentation_section import DocumentationSection

_logger = logging.getLogger(__name__)


# TODO: we won't need this when the playground agent will be directly connected to update to date WorkflowAI docs
DEFAULT_DOC_SECTIONS: list[DocumentationSection] = [
    DocumentationSection(
        title="Business Associate Agreements (BAA)",
        content="WorkflowAI has signed BBAs with all the providers offered on the WorkflowAI platform (OpenAI, Anthropic, Fireworks, etc.).",
    ),
    DocumentationSection(
        title="Hosting of DeepSeek models",
        content="Also alse the DeepSeek models offered by WorkflowAI are US hosted.",
    ),
]


def _extract_doc_title(file_name: str) -> str:
    base: str = file_name.rsplit(".", 1)[0]
    prefix: str = "docs_workflowai_com_"
    if base.startswith(prefix):
        base = base[len(prefix) :]
    return base.replace("_", " ").title()


class DocumentationService:
    def get_all_doc_sections(self) -> list[DocumentationSection]:
        doc_sections: list[DocumentationSection] = []
        for file in os.listdir("docs"):
            with open(os.path.join("docs", file), "r") as f:
                doc_sections.append(
                    DocumentationSection(title=_extract_doc_title(file), content=f.read()),
                )
        return doc_sections

    @classmethod
    def build_api_docs_prompt(cls, folder_name: str = "docs") -> str:
        api_docs: str = ""

        for file in os.listdir(folder_name):
            with open(os.path.join(folder_name, file), "r") as f:
                api_docs += f"{file}\n{f.read()}\n\n"

        return api_docs

    async def get_relevant_doc_sections(
        self,
        chat_messages: list[MetaAgentChatMessage],
        agent_instructions: str,
    ) -> list[DocumentationSection]:
        all_doc_sections: list[DocumentationSection] = self.get_all_doc_sections()

        try:
            relevant_doc_sections: list[str] = (
                await pick_relevant_documentation_sections(
                    PickRelevantDocumentationSectionsInput(
                        available_doc_sections=all_doc_sections,
                        chat_messages=chat_messages,
                        agent_instructions=agent_instructions,
                    ),
                )
            ).relevant_doc_sections
        except Exception as e:
            _logger.exception("Error getting relevant doc sections", exc_info=e)
            # Fallback on all doc sections (no filtering)
            relevant_doc_sections: list[str] = [doc_category.title for doc_category in all_doc_sections]

        return DEFAULT_DOC_SECTIONS + [
            document_section for document_section in all_doc_sections if document_section.title in relevant_doc_sections
        ]
