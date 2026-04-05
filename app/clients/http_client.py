from typing import Any

import aiohttp


class HttpClient:
    def __init__(self, base_url: str, auth_url: str, credentials: dict[str, str]) -> None:
        self._base_url = base_url
        self._auth_url = auth_url
        self._credentials = credentials
        self._token: str | None = None
        self._session: aiohttp.ClientSession | None = None

    async def _fetch_token(self) -> Any:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={"Content-Type": "application/json"},
        ) as session:
            async with session.post(self._auth_url, json=self._credentials) as response:
                resp = await response.json()
                return resp["access_token"]

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._token is None:
            self._token = await self._fetch_token()
            self._session = aiohttp.ClientSession(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            )
        return self._session

    async def _refresh_token(self) -> None:
        self._token = await self._fetch_token()
        if self._session:
            await self._session.close()
        self._session = aiohttp.ClientSession(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=10),
        )

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None  # ignore: no-untyped-def

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        session = await self._ensure_session()
        async with session.request(method, endpoint, **kwargs) as response:
            if response.status == 401:
                await self._refresh_token()
                if self._session:
                    async with self._session.request(method, endpoint, **kwargs) as retry:
                        return await retry.json()
            return await response.json()
