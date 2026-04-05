from typing import Any

from app.clients.http_client import HttpClient


class ApiHttpClient(HttpClient):
    def __init__(self, base_url: str, username: str, password: str) -> None:
        super().__init__(
            base_url=base_url,
            auth_url=f"{base_url}/auth/token",
            credentials={"username": username, "password": password},
        )

    async def add_event_vulnerabilities(self, body: dict[str, Any]) -> Any:
        endpoint = "/api/v1/s3/event-receiver/it-dashboard/cyber-security-vulnerabilities/upload"
        return await self._request("POST", endpoint, json=body)

    async def add_batch_vulnerabilities(self, body: dict[str, Any]) -> Any:
        endpoint = "/api/v1/s3/batch-receiver/it-dashboard/cyber-security-vulnerabilities/upload"
        return await self._request("POST", endpoint, json=body)

    async def add_single_event_vulnerability(self, body: dict[str, Any]) -> Any:
        endpoint = "/api/v1/s3/single-event-receiver/it-dashboard/cyber-security-vulnerabilities/upload"
        return await self._request("POST", endpoint, json=body)

    async def get_vulnerability(self, key: str) -> Any:
        return await self._request("GET", f"/api/v1/s3/system/{key}")

    async def delete_vulnerability(self, key: str) -> Any:
        return await self._request("DELETE", f"/api/v1/s3/system/{key}")
