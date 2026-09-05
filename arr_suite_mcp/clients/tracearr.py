"""Tracearr client — streaming access manager (account sharing detection)."""

import logging
from typing import Any, Optional
import httpx

from .base import ArrClientError, ArrClientConnectionError, ArrClientAuthError

logger = logging.getLogger(__name__)

BASE_PATH = "/api/v1/public"


class TracearrClient:
    """Client for the Tracearr public API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    @property
    def service_name(self) -> str:
        return "tracearr"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self.base_url}{BASE_PATH}/{path.lstrip('/')}"

    async def _get(self, path: str, params: Optional[dict] = None) -> Any:
        try:
            r = await self.client.get(self._url(path), headers=self._headers(), params=params)
            if r.status_code == 401:
                raise ArrClientAuthError("Tracearr: invalid API key")
            if r.status_code >= 400:
                raise ArrClientError(f"Tracearr: HTTP {r.status_code} - {r.text}")
            return r.json()
        except httpx.ConnectError as e:
            raise ArrClientConnectionError(f"Tracearr: could not connect to {self.base_url}") from e
        except httpx.TimeoutException as e:
            raise ArrClientConnectionError(f"Tracearr: request timed out") from e

    async def _post(self, path: str, json: Optional[dict] = None) -> Any:
        try:
            r = await self.client.post(self._url(path), headers=self._headers(), json=json or {})
            if r.status_code == 401:
                raise ArrClientAuthError("Tracearr: invalid API key")
            if r.status_code >= 400:
                raise ArrClientError(f"Tracearr: HTTP {r.status_code} - {r.text}")
            return r.json() if r.content else None
        except httpx.ConnectError as e:
            raise ArrClientConnectionError(f"Tracearr: could not connect to {self.base_url}") from e

    async def health(self) -> dict:
        return await self._get("health")

    async def stats(self) -> dict:
        return await self._get("stats")

    async def streams(self) -> dict:
        return await self._get("streams")

    async def users(self) -> dict:
        return await self._get("users")

    async def violations(self, limit: int = 25, offset: int = 0, resolved: Optional[bool] = None) -> dict:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if resolved is not None:
            params["resolved"] = str(resolved).lower()
        return await self._get("violations", params=params)

    async def history(self, limit: int = 25, offset: int = 0, username: Optional[str] = None) -> dict:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if username:
            params["username"] = username
        return await self._get("history", params=params)

    async def terminate_stream(self, stream_id: str, reason: Optional[str] = None) -> dict:
        body: dict[str, Any] = {}
        if reason:
            body["reason"] = reason
        return await self._post(f"streams/{stream_id}/terminate", json=body)

    async def close(self) -> None:
        await self.client.aclose()
