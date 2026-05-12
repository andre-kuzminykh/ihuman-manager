"""
DigestAPI.

## Трассируемость
Feature: F007, F011
Scenarios: SC018, SC019, SC028
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

    async def evening_for_user(
        self, user_id: int, day: datetime | None = None
    ) -> dict:
        """Вечерний дайджест (F011)."""
        params = {}
        if day is not None:
            params["day"] = day.isoformat()
        return await self._request("GET", f"/digest/{user_id}/evening", params=params)
