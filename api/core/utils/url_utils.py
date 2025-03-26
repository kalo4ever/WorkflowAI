import asyncio
import logging
import re
from typing import Match, cast

from core.domain.url_content import URLContent, URLStatus
from core.tools.browser_text.browser_text_tool import browser_text_with_proxy_setting

logger = logging.getLogger(__name__)

# Simple regex to find email addresses
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@([a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]\.[a-zA-Z0-9.]{2,})"

# Updated regex that handles paths correctly
URL_REGEX = r"(https?:\/\/|www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]\.[a-zA-Z0-9.]{2,})(?:\/[^\s'\"]*)?"


def find_urls_in_text(text: str) -> list[str]:
    if text == "":
        return []

    # First, find all email domains to exclude
    email_domains = set(re.findall(EMAIL_REGEX, text))

    # Find all potential URLs
    url_matches: list[Match[str]] = list(re.finditer(URL_REGEX, text))

    cleaned_urls: list[str] = []
    for match in url_matches:
        url = match.group(0)
        domain = match.group(2)

        # Clean up trailing punctuation
        url = url.rstrip("'\".,;:!?)")

        # Skip if this is just a domain from an email address and has no path
        path_part = url[len(domain) + (0 if match.group(1) is None else len(match.group(1))) :]
        if domain in email_domains and not path_part:
            continue

        # Add https:// to URLs that don't have a protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        cleaned_urls.append(url)

    return cleaned_urls


async def fetch_urls_content(urls: list[str]) -> list[URLContent]:
    if not urls:
        return []

    # Use asyncio.gather to fetch all URLs concurrently
    results = await asyncio.gather(
        *[_fetch_single_url_content(url) for url in urls],
        return_exceptions=True,
    )

    url_contents: list[URLContent] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.exception(
                "Error fetching URL content",
                extra={"url": urls[i]},
            )
            # Create an unreachable URL content entry
            url_contents.append(
                URLContent(
                    url=urls[i],
                    content=None,
                    status=URLStatus.UNREACHABLE,
                ),
            )
        else:
            # Result is already a URLContent instance
            url_contents.append(cast(URLContent, result))

    return url_contents


async def _fetch_single_url_content(url: str) -> URLContent:
    try:
        # We use the "premium" proxy setting to get a good balance between speed and reliability, since '_fetch_single_url_content' is used on the agent builder
        content = await browser_text_with_proxy_setting(url, proxy_setting="premium")
        # If content is empty or just whitespace, consider it unreachable
        if not content or content.strip() == "":
            return URLContent(
                url=url,
                content=None,
                status=URLStatus.UNREACHABLE,
            )

        return URLContent(
            url=url,
            content=content,
            status=URLStatus.REACHABLE,
        )
    except Exception:
        logger.exception(
            "Error fetching URL content",
            extra={"url": url},
        )
        return URLContent(
            url=url,
            content=None,
            status=URLStatus.UNREACHABLE,
        )


async def extract_and_fetch_urls(text: str) -> list[URLContent]:
    # Extract URLs from the text
    urls = find_urls_in_text(text)

    # Fetch content for each URL
    return await fetch_urls_content(urls)
