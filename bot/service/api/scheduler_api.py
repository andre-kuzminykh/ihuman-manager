"""
SchedulerAPI.

## Трассируемость
Feature: F003, F006, F007
Scenarios: SC007, SC015, SC017, SC018, SC019
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service.api.base_api import BaseAPI


class SchedulerAPI(BaseAPI):
    async def tick(self, *, now: datetime | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if now is not None:
            body["now"] = now.isoformat()
        return await self._request("POST", "/scheduler/tick", json=body)
