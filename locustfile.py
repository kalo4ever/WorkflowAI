import os
from typing import Any

from dotenv import load_dotenv
from locust import HttpUser, task

load_dotenv(override=True)


class RunUser(HttpUser):
    host = os.environ["TEST_E2E_API_URL"]

    def on_start(self):
        # Add the Authorization header to the session headers
        self.client.headers = {"Authorization": f"Bearer {os.environ['TEST_E2E_API_TOKEN']}"}

    def _run_task(
        self,
        task_id: str,
        schema_id: int,
        version: str | int | dict[str, Any],
        input: dict[str, Any],
        use_cache: bool = False,
    ):
        self.client.post(
            f"/v1/_/agents/{task_id}/schemas/{schema_id}/run",
            json={
                "task_input": input,
                "version": version,
                "use_cache": "auto" if use_cache else "never",
            },
            timeout=120,
        )

    @task
    def run_analyze_book_characters_production(self):
        self._run_task(
            "analyze-book-characters",
            1,
            {"model": "claude-3-haiku-20240307", "provider": "anthropic"},
            {"book_title": "The Shadow of the Wind"},
            use_cache=False,
        )

    # @task
    # def fetch_runs(self):
    #     self.client.get("/_/agents/citytocapital/schemas/1/runs?limit=10000")
