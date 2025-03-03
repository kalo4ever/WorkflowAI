import pytest

from core.domain.errors import InvalidFileError
from core.utils.file_utils.file_utils import extract_text_from_file_base64, guess_content_type
from tests.utils import fixture_bytes


# Tests
def test_extract_text_from_file_base64_txt():
    base64_data = "VGhpcyBpcyBhIHNhbXBsZSAudHh0IGZpbGUK"  # manually computed from a .txt file
    result = extract_text_from_file_base64(base64_data)
    assert (
        result
        == """This is a sample .txt file
"""
    )


def test_extract_text_from_file_base64_md():
    base64_data = "IyBNYXJrZG93biB0aXRsZQpNYXJrIGRvd24gY29udGVudAo="  # manually computed from a .md file
    result = extract_text_from_file_base64(base64_data)
    assert (
        result
        == """# Markdown title
Mark down content
"""
    )


def test_extract_text_from_file_base64_csv():
    base64_data = "UHJpY2UsVW5pdHMsVG90YWwgQ29zdAoxMCwxLDEwCjEsMiwyCg=="
    result = extract_text_from_file_base64(base64_data)
    assert (
        result
        == """Price,Units,Total Cost
10,1,10
1,2,2
"""
    )


def test_extract_text_from_file_base64_html():
    base64_data = "PGh0bWw+Cgo8Ym9keT4KICAgIDxoMT5IZWxsbzwvaDE+CjwvYm9keT4KCjwvaHRtbD4="
    result = extract_text_from_file_base64(base64_data)
    assert (
        result
        == """<html>

<body>
    <h1>Hello</h1>
</body>

</html>"""
    )


def test_extract_text_from_file_base64_json():
    base64_data = "ewogICAgImtleSI6ICJ2YWx1ZSIKfQ=="
    result = extract_text_from_file_base64(base64_data)
    assert (
        result
        == """{
    "key": "value"
}"""
    )


def test_extract_text_from_file_base64_empty_input():
    assert extract_text_from_file_base64("") == ""


def test_extract_text_from_file_invalid_input_unicode():
    with pytest.raises(InvalidFileError, match="unicode"):
        extract_text_from_file_base64("aaaa")


def test_extract_text_from_file_invalid_input_base64():
    invalid_base64_data = "!!!invalid_base64!!!"
    with pytest.raises(InvalidFileError, match="base64"):
        extract_text_from_file_base64(invalid_base64_data)


class TestGuessContentType:
    def test_guess_webp(self):
        data = fixture_bytes("files/test.webp")
        assert guess_content_type(data, mode="image") == "image/webp"

    def test_guess_png(self):
        data = fixture_bytes("files/test.png")
        assert guess_content_type(data, mode="image") == "image/png"
