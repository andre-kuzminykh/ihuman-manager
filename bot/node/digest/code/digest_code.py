"""
DigestCode.

## Трассируемость
Feature: F007
Scenarios: SC018, SC019
"""

from __future__ import annotations

from service.api.digest_api import DigestAPI


class DigestCode:
    def __init__(self, api: DigestAPI | None = None) -> None:
        self._api = api or DigestAPI()

    async def run(self, user_id: int) -> dict:
        digest = await self._api.for_user(user_id)
        return {"answer_name": "digest", "data": {"digest": digest}}
