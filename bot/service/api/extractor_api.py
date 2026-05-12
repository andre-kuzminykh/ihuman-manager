"""
ExtractorAPI.

## Трассируемость
Feature: F001, F005
"""

from __future__ import annotations

from datetime import datetime

from service.api.base_api import BaseAPI


class ExtractorAPI(BaseAPI):
    async def extract(
        self,
        *,
        text: str,
        now: datetime | None = None,
        context_messages: list[dict] | None = None,
    ) -> dict:
        body = {"text": text, "context_messages": context_messages or []}
        if now is not None:
            body["now"] = now.isoformat()
        return await self._request("POST", "/extract", json=body)
