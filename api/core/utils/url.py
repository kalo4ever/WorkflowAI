import re
import urllib.parse


def parse_url(url: str) -> tuple[str, str, str, dict[str, list[str]]]:
    """Extract the four components of a URL (schema, domain, path, and query)."""

    parsed_url = urllib.parse.urlparse(url)

    # Extract the four components of the URL
    schema, domain, path, query = (
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        urllib.parse.parse_qs(parsed_url.query),
    )

    # Remove trailing slashes
    path = path.rstrip("/")

    return schema, domain, path, query


def is_valid_http_url(value: str) -> bool:
    """
    Validates a URL string to ensure it is a well-formed URL with either http or https scheme,
    contains a valid domain with a TLD.

    Parameters:
    - value (str): The URL string to validate.

    Returns:
    - str: The validated URL string if it is valid.

    Raises:
    - ValueError: If the URL is not valid, the scheme is not http or https, or the domain is missing or invalid.
    """
    try:
        schema, domain, _, _ = parse_url(value)  # Use urlparse to parse the URL
        if schema not in {"http", "https"}:
            return False  # Invalid schema
        if not domain:
            raise ValueError("URL must have a domain")

        # Regular expression for validating domain with TLD
        domain_regex = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")
        if not domain_regex.match(domain):
            return False  # Invalid domain (no TLD or invalid characters in domain name)

    except ValueError:
        return False  # URL is not parsable

    return True


def are_urls_equal(url_1: str, url_2: str) -> bool:
    """
    Compare two URLs.
    Compares the four components of an URLs (schema, domain, path, and query).
    Also removes trailing slashes from the path.
    """

    schema_1, domain_1, path_1, query_1 = parse_url(url_1)
    schema_2, domain_2, path_2, query_2 = parse_url(url_2)

    if not schema_1 == schema_2:
        return False  # Different schemas (e.g. http:// vs https://)
    if not domain_1 == domain_2:
        return False  # Different domains
    if not path_1 == path_2:
        return False  # Different paths
    if not query_1 == query_2:
        return False  # Different query parameters

    # All the four components are the same, so the URLs are considered equal
    return True
