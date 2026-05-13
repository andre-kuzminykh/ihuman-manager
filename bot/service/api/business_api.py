"""
BusinessAPI — HTTP-клиент business connections.

## Трассируемость
Feature: F018
Scenarios: SC036, SC037
"""

from __future__ import annotations

from service.api.base_api import APIError, BaseAPI


class BusinessAPI(BaseAPI):
    async def upsert_connection(
        self,
        *,
        business_connection_id: str,
        owner_user_id: int,
        is_enabled: bool = True,
        can_reply: bool = False,
    ) -> dict:
        return await self._request(
            "POST",
            "/business/connections",
            json={
                "business_connection_id": business_connection_id,
                "owner_user_id": owner_user_id,
                "is_enabled": is_enabled,
                "can_reply": can_reply,
            },
        )

    async def get_owner(self, business_connection_id: str) -> int | None:
        try:
            obj = await self._request(
                "GET", f"/business/connections/{business_connection_id}"
            )
        except APIError as exc:
            if exc.status_code == 404:
                return None
            raise
        if not obj.get("is_enabled"):
            return None
        return obj.get("owner_user_id")
