"""
BaseAPI — общий HTTP-клиент. Все API-клиенты наследуются.

## Трассируемость
Все фичи (это инфраструктура).
"""

from __future__ import annotations

from typing import Any

import httpx

from core.config import config


class APIError(Exception):
    def __init__(self, status_code: int, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class BaseAPI:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or config.backend_base).rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Any:
        async with self._client() as client:
            resp = await client.request(method, path, **kwargs)
        if resp.status_code >= 400:
            body = self._safe_json(resp)
            raise APIError(
                resp.status_code,
                body.get("message") if isinstance(body, dict) else resp.text,
                body.get("code") if isinstance(body, dict) else None,
            )
        if resp.status_code == 204:
            return None
        return self._safe_json(resp)

    @staticmethod
    def _safe_json(resp: httpx.Response) -> Any:
        try:
            return resp.json()
        except Exception:
            return resp.text
