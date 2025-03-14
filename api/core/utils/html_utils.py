import re
from html.parser import HTMLParser
from typing import Any


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.texts: list[str] = []
        self.skip_data = False
        self.current_href = ""

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in ["script", "style"]:
            self.skip_data = True
        elif tag == "a":
            href = dict(attrs).get("href")  # Capture href (URL) attribute from <a> tags
            if href:
                self.current_href = href

    def handle_endtag(self, tag: str) -> None:
        if tag in ["script", "style"]:
            self.skip_data = False
        elif tag == "a" and self.current_href:
            self.texts.append(
                f"(URL: {self.current_href})",
            )  # Insert the href (URL) attribute from <a> tags after the link text
            self.current_href = ""

    def handle_data(self, data: str) -> None:
        if not self.skip_data:
            self.texts.append(data)

    def get_data(self) -> str:
        combined_text = " ".join(self.texts).strip()
        # Replace multiple spaces with a single space
        return re.sub(r"\s+", " ", combined_text)


def get_text_from_html(html_content: str) -> str:
    """Extract plain text from HTML content, removing JS, CSS, and double spaces."""
    extractor = TextExtractor()
    extractor.feed(html_content)
    return extractor.get_data()


def contains_html(str_content: str) -> bool:
    """Check if the given content contains HTML tags."""
    return "<html" in str_content and "</html" in str_content
