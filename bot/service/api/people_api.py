"""
PeopleAPI — HTTP-клиент контактов.

## Трассируемость
Feature: F020
"""

from __future__ import annotations

from service.api.base_api import BaseAPI


class PeopleAPI(BaseAPI):
    async def touch(
        self,
        *,
        telegram_user_id: int | None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_bot: bool = False,
        language_code: str | None = None,
        is_premium: bool = False,
    ) -> dict | None:
        return await self._request(
            "POST",
            "/people/touch",
            json={
                "telegram_user_id": telegram_user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_bot": is_bot,
                "language_code": language_code,
                "is_premium": is_premium,
            },
        )

    async def list_all(self) -> list[dict]:
        return await self._request("GET", "/people/") or []
