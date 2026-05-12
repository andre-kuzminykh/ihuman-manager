"""
PendingTasksAPI.

## Трассируемость
Feature: F005
Scenarios: SC012, SC014
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service.api.base_api import BaseAPI


class PendingTasksAPI(BaseAPI):
    async def list(self, owner_user_id: int, only_unapproved: bool = True) -> list[dict]:
        return await self._request(
            "GET",
            "/pending-tasks",
            params={"owner_user_id": owner_user_id, "only_unapproved": only_unapproved},
        ) or []

    async def get(self, pending_id: int) -> dict:
        return await self._request("GET", f"/pending-tasks/{pending_id}")

    async def update(
        self,
        pending_id: int,
        *,
        title: str | None = None,
        text: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
        draft: dict[str, Any] | None = None,
    ) -> dict:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if text is not None:
            body["text"] = text
        if deadline is not None:
            body["deadline"] = deadline.isoformat()
        if direction_id is not None:
            body["direction_id"] = direction_id
        if draft is not None:
            body["draft"] = draft
        return await self._request("PUT", f"/pending-tasks/{pending_id}", json=body)

    async def approve(self, pending_id: int) -> dict:
        return await self._request("POST", f"/pending-tasks/{pending_id}/approve")

    async def reject(self, pending_id: int) -> dict:
        return await self._request("POST", f"/pending-tasks/{pending_id}/reject")
