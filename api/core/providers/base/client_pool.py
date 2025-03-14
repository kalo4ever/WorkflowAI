import time

import httpx


class ClientWithLastUsed:
    def __init__(self):
        self._client = httpx.AsyncClient()
        self._last_used = time.time()

    def update_last_used(self):
        self._last_used = time.time()
        return self._client

    async def close(self):
        await self._client.aclose()

    @property
    def last_used(self) -> float:
        return self._last_used


class ClientPool:
    def __init__(self):
        self.clients: dict[str, ClientWithLastUsed] = {}

    def get(self, url: str) -> httpx.AsyncClient:
        domain = httpx.URL(url).host
        client = self.clients.get(domain)
        if client is None:
            client = ClientWithLastUsed()
            self.clients[domain] = client
        return client.update_last_used()

    async def close(self, domain: str):
        try:
            client = self.clients.pop(domain)
            await client.close()
        except KeyError:
            pass

    async def purge(self):
        for client in self.clients.values():
            # Close clients that haven't been used in the last hour
            if client.last_used < time.time() - 3600:
                await client.close()
