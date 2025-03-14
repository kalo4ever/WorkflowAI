from core.utils.html_utils import get_text_from_html


def test_returns_string() -> None:
    html = "<html><body>Test</body></html>"
    result = get_text_from_html(html)
    assert isinstance(result, str)


def test_removes_javascript_and_css() -> None:
    html = "<html><head><style>CSS content</style></head><body><script>JS content</script>Text</body></html>"
    result = get_text_from_html(html)
    assert "CSS content" not in result
    assert "JS content" not in result
    assert "Text" in result


def test_handles_URL_correctly() -> None:
    html = "http://www.example.com"
    expected = "http://www.example.com"
    result = get_text_from_html(html)
    assert result == expected


def test_handles_raw_strings_correctly() -> None:
    html = "test string"
    expected = "test string"
    result = get_text_from_html(html)
    assert result == expected


def test_handles_mixed_content_correctly() -> None:
    html = "Plain text <b>with</b> HTML."
    expected = "Plain text with HTML."
    result = get_text_from_html(html)
    assert result == expected


def test_extracts_text_correctly() -> None:
    html = "<div><p>First paragraph.</p><p>Second paragraph.</p></div>"
    expected = "First paragraph. Second paragraph."
    result = get_text_from_html(html)
    assert result == expected


def test_extracts_outlook_calendar_event_description_correctly() -> None:
    html = """
    <html>\r\n<head>\r\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n</head>\r\n<body>\r\n<div style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:12pt; color:rgb(0,0,0)">\r\nSome HTML content from an Outlook meeting</div>\r\n</body>\r\n</html>\r\n\n
    """
    expected = "Some HTML content from an Outlook meeting"
    result = get_text_from_html(html)
    assert result == expected


def test_extract_a_tag_url() -> None:
    # HTML content with <a> tags
    html = '<html><body><p>Visit <a href="http://example1.com">Example Site 1</a> and <a href="http://example2.com">Example Site 2</a> sites.</p></body></html>'

    # Expected result should include the URL after the link text
    expected = "Visit Example Site 1 (URL: http://example1.com) and Example Site 2 (URL: http://example2.com) sites."

    result = get_text_from_html(html)
    assert result == expected


def contains_html(str_content: str) -> bool:
    """Check if the given content contains HTML tags."""
    return "<html" in str_content and "</html" in str_content


def test_contains_html_with_html_content():
    html_content = "<html><body><p>This is a paragraph.</p></body></html>"
    assert contains_html(html_content) is True


def test_contains_html_with_html_attribute():
    html_content = "<html lang='en'><body><p>This is a paragraph.</p></body></html>"
    assert contains_html(html_content) is True


def test_contains_html_with_partial_html_content():
    partial_html_content = "<html><body>This is some text."
    assert contains_html(partial_html_content) is False


def test_contains_html_with_no_html_content():
    no_html_content = "This is a plain text string."
    assert contains_html(no_html_content) is False


def test_contains_html_with_nested_html_tags():
    nested_html_content = "<html><body><div><p>Nested tags.</p></div></body></html>"
    assert contains_html(nested_html_content) is True


def test_contains_html_with_empty_string():
    empty_content = ""
    assert contains_html(empty_content) is False


def test_contains_html_with_html_like_text():
    html_like_text = "Some text: <html> and </html>"
    assert contains_html(html_like_text) is True
