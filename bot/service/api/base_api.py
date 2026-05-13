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
    DEFAULT_TIMEOUT = 30.0
    SLOW_PATHS = ("/llm-edit", "/extract", "/voice/transcribe", "/messages/ingest")

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or config.backend_base).rstrip("/")

    def _timeout_for(self, path: str) -> float:
        # LLM/voice идут к OpenAI — даём больше времени.
        if any(p in path for p in self.SLOW_PATHS):
            return 120.0
        return self.DEFAULT_TIMEOUT

    def _client(self, timeout: float) -> httpx.AsyncClient:
        # follow_redirects=True — FastAPI 0.115 редиректит /tasks → /tasks/
        return httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout, follow_redirects=True
        )

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Any:
        timeout = self._timeout_for(path)
        async with self._client(timeout) as client:
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
