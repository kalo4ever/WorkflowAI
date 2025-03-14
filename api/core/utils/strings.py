import base64
import re
import string
import unicodedata


def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def split_words(input_str: str) -> list[str]:
    name = re.sub("([a-z])([A-Z])", r"\1 \2", input_str)
    return re.split(r"\s|-|_", name)


def to_pascal_case(input_str: str) -> str:
    components = split_words(input_str)
    return "".join(x.title() for x in components)


def to_snake_case(input_str: str) -> str:
    components = split_words(input_str)
    return "_".join(x.lower() for x in components)


def to_kebab_case(input_str: str) -> str:
    components = split_words(input_str)
    return "-".join(x.lower() for x in components)


def b64_urldecode(input_str: str) -> bytes:
    """Decode a base64url encoded string and accepts no padding."""
    # Fix padding
    rem = len(input_str) % 4
    if rem > 0:
        input_str += "=" * (4 - rem)
    return base64.urlsafe_b64decode(input_str)


def normalize(s: str, case_sensitive: bool = False, remove_punctuation: bool = True):
    """Normalize a string for comparison by removing diacritics, making it case insensitive, and removing punctuation."""
    # Remove diacritics
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    if not case_sensitive:
        # Make case insensitive
        s = s.lower()
    # Remove punctuation
    if remove_punctuation:
        s = s.translate(str.maketrans("", "", string.punctuation))
    # Remove duplicate whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def slugify(s: str) -> str:
    n = normalize(s, case_sensitive=True, remove_punctuation=False)
    n = to_kebab_case(n)
    # Making sure by removing any non-url safe characters
    return re.sub(r"[^a-z0-9-]", "", n).replace("--", "-")


def is_url_safe(input_str: str) -> bool:
    return re.match(r"^[a-zA-Z0-9_-]+$", input_str) is not None


def remove_empty_lines(text: str) -> str:
    return re.sub(r"\n+", "\n", text)
