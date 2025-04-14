import logging
from datetime import date, timedelta
from typing import Literal, NamedTuple

import httpx

from core.agents.uptime_extraction_agent import UptimeExtractorAgentInput, uptime_extraction_agent
from core.tools.browser_text.browser_text_tool import browser_text
from core.utils.redis_cache import redis_cached


class UptimeInfo(NamedTuple):
    uptime: float | None
    since: date | None
    source: str


ServiceName: Literal["workflowai", "openai"]


class UptimeService:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    def _check_date_diff(self, from_date: date, to_date: date, tolerance: int, service_name: str):
        if from_date - to_date > timedelta(days=tolerance):
            self._logger.warning(
                "Uptime date difference is greater than tolerance",
                extra={
                    "from_date": from_date,
                    "to_date": to_date,
                    "tolerance": tolerance,
                    "service_name": service_name,
                },
            )

    async def _get_openai_chat_api_component_id(self) -> str | None:
        OPENAI_STATUS_URL = "https://status.openai.com/proxy/status.openai.com"
        CHAT_API_COMPONENT_NAME = "Chat"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPENAI_STATUS_URL)
                response.raise_for_status()
                status_page_content = response.json()

                for component in status_page_content.get("summary", {}).get("components", []):
                    if component.get("name") == CHAT_API_COMPONENT_NAME:
                        return component.get("id")
                return None
        except Exception as e:
            self._logger.exception("Error finding Chat API component ID", exc_info=e)
            return None

    async def _get_open_ai_component_uptime(
        self,
        current_date: date,
        component_id: str,
    ) -> tuple[float | None, date | None]:
        OPENAI_STATUS_DETAILS_URL = "https://status.openai.com/proxy/status.openai.com/component_impacts"

        start_from = current_date - timedelta(days=90)
        start_at = f"{start_from.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        end_at = f"{current_date.strftime('%Y-%m-%d')}T00%3A00%3A00.00Z"
        query_str = f"?start_at={start_at}&end_at={end_at}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPENAI_STATUS_DETAILS_URL + query_str)
                response.raise_for_status()
                status_page_content = response.json()

                for component in status_page_content.get("component_uptimes", {}):
                    if component.get("component_id") == component_id:
                        return (component.get("uptime"), start_from)

            raise Exception("Can't find component in OpenAI reponse")

        except Exception as e:
            self._logger.exception("Error getting OpenAI component uptime", exc_info=e)
            return None, None

    async def _manually_scrape_openai(self) -> tuple[float | None, date | None]:
        chat_component_id = await self._get_openai_chat_api_component_id()
        if chat_component_id is None:
            return None, None

        uptime, since = await self._get_open_ai_component_uptime(date.today(), chat_component_id)
        return uptime, since

    async def _get_uptime_info(
        self,
        status_page_url: str,
        extraction_instructions: str | None = None,
    ) -> tuple[float | None, date | None]:
        try:
            status_page_content = await browser_text(status_page_url)
            uptime_extraction_run = await uptime_extraction_agent(
                UptimeExtractorAgentInput(
                    status_page_content=status_page_content,
                    extraction_instructions=extraction_instructions,
                ),
            )

            uptime = uptime_extraction_run.output.uptime
            if uptime is None:
                self._logger.error(
                    "No uptime extracted",
                    extra={"status_page_url": status_page_url, "extraction_run_id": uptime_extraction_run.id},
                )

            since = uptime_extraction_run.output.since
            since_date = None
            if since is None:
                self._logger.error(
                    "No uptime since extracted",
                    extra={"status_page_url": status_page_url, "extraction_run_id": uptime_extraction_run.id},
                )
            else:
                try:
                    since_date = date.fromisoformat(since)
                except Exception as e:
                    self._logger.exception(
                        "Invalid since date",
                        extra={
                            "since": since,
                            "status_page_url": status_page_url,
                            "extraction_run_id": uptime_extraction_run.id,
                        },
                        exc_info=e,
                    )
            return uptime, since_date
        except Exception as e:
            self._logger.exception(
                "Error extracting uptime for",
                extra={"status_page_url": status_page_url},
                exc_info=e,
            )
            return None, None

    @redis_cached(expiration_seconds=60 * 60)  # TTL = 1h
    async def get_workflowai_uptime(self) -> UptimeInfo:
        URL = "https://status.workflowai.com"
        uptime, since = await self._get_uptime_info(
            URL,
            "Extract the API uptime",
        )

        # BetterStack should display uptime from 90 days from now. So we allow a small difference of 5 days
        if since is not None:
            self._check_date_diff(since, date.today() - timedelta(days=90), 5, "workflowai")
        return UptimeInfo(uptime=uptime, since=since, source=URL)

    @redis_cached(expiration_seconds=60 * 60)  # TTL = 1h
    async def get_openai_uptime(self) -> UptimeInfo:
        URL = "https://status.openai.com"

        # First try to get the uptime from the manually scraped data, more precise becasue it can get the exact 'Chat API' uptime
        uptime, since = await self._manually_scrape_openai()
        if uptime is not None and since is not None:
            return UptimeInfo(uptime=uptime, since=since, source=URL)

        # If that fails, directly scrape the status page, but only allows to get the overall uptime of all APIs (completions, embeddings, etc) so less relevant
        uptime, since = await self._get_uptime_info(
            URL,
            "Extract the 'APIs' uptime, DO NOT EXTRACT the uptime for 'ChatGPT'",
        )
        if since is not None:
            # On this degraded scraping mode we can only know the month of start of uptime so we allow 32 days of tolerance.
            self._check_date_diff(since, date.today() - timedelta(days=90), 32, "openai")
        return UptimeInfo(uptime=uptime, since=since, source=URL)
