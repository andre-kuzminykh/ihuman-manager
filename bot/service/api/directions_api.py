"""
DirectionsAPI.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024
"""

from __future__ import annotations

from typing import Any

from service.api.base_api import BaseAPI


class DirectionsAPI(BaseAPI):
    async def create(self, *, user_id: int, name: str, is_favorite: bool = False) -> dict:
        return await self._request(
            "POST",
            "/directions",
            json={"user_id": user_id, "name": name, "is_favorite": is_favorite},
        )

    async def list(self, user_id: int) -> list[dict]:
        return await self._request("GET", "/directions", params={"user_id": user_id}) or []

    async def update(self, direction_id: int, **fields: Any) -> dict:
        return await self._request("PUT", f"/directions/{direction_id}", json=fields)

    async def delete(self, direction_id: int) -> None:
        await self._request("DELETE", f"/directions/{direction_id}")

    async def set_favorite(self, direction_id: int, value: bool) -> dict:
        method = "POST" if value else "DELETE"
        return await self._request(method, f"/directions/{direction_id}/favorite")
