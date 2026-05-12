"""
DigestAPI.

## Трассируемость
Feature: F007
Scenarios: SC018, SC019
"""

from __future__ import annotations

from datetime import datetime

from service.api.base_api import BaseAPI


class DigestAPI(BaseAPI):
    async def for_user(self, user_id: int, day: datetime | None = None) -> dict:
        params = {}
        if day is not None:
            params["day"] = day.isoformat()
        return await self._request("GET", f"/digest/{user_id}", params=params)
