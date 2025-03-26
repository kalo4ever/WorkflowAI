import pytest

from api.services.documentation_service import _extract_doc_title  # type: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    "file_name, expected_title",
    [
        ("docs_workflowai_com_getting_started.md", "Getting Started"),
        ("docs_workflowai_com_introduction.md", "Introduction"),
        ("some_other_name.md", "Some Other Name"),
    ],
)
def test_extract_doc_title(file_name: str, expected_title: str) -> None:
    assert _extract_doc_title(file_name) == expected_title
