import os

import httpx

TIMEOUT_SECONDS = 30


async def run_google_search(query: str) -> str:
    """Runs a Google search and returns the results in JSON format."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": os.environ["SERPER_API_KEY"], "Content-Type": "application/json"},
            json={"q": query},
            timeout=TIMEOUT_SECONDS,
        )
        return response.text
