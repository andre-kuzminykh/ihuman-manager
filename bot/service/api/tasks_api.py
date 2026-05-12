"""
TasksAPI — HTTP-клиент задач.

## Трассируемость
Feature: F001–F004, F006, F008, F009
Scenarios: SC001, SC002, SC003, SC006, SC008, SC009, SC010, SC016, SC020
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service.api.base_api import BaseAPI


class TasksAPI(BaseAPI):
    async def create(
        self,
        *,
        user_id: int,
        text: str,
        chat_id: int | None = None,
        source_message_id: int | None = None,
        source_kind: str = "text",
        title: str | None = None,
        deadline: datetime | None = None,
        direction_id: int | None = None,
    ) -> dict:
        body: dict[str, Any] = {
            "user_id": user_id,
            "text": text,
            "source_kind": source_kind,
        }
        if chat_id is not None:
            body["chat_id"] = chat_id
        if source_message_id is not None:
            body["source_message_id"] = source_message_id
        if title:
            body["title"] = title
        if deadline:
            body["deadline"] = deadline.isoformat()
        if direction_id is not None:
            body["direction_id"] = direction_id
        return await self._request("POST", "/tasks", json=body)

    async def list(
        self,
        *,
        user_id: int,
        status: list[str] | None = None,
        direction_id: int | None = None,
        favorite_only: bool = False,
        deadline_before: datetime | None = None,
        deadline_after: datetime | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {"user_id": user_id, "favorite_only": favorite_only}
        if status:
            params["status"] = status
        if direction_id is not None:
            params["direction_id"] = direction_id
        if deadline_before is not None:
            params["deadline_before"] = deadline_before.isoformat()
        if deadline_after is not None:
            params["deadline_after"] = deadline_after.isoformat()
        return await self._request("GET", "/tasks", params=params) or []

    async def get(self, task_id: int) -> dict:
        return await self._request("GET", f"/tasks/{task_id}")

    async def update(self, task_id: int, **fields: Any) -> dict:
        clean = {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in fields.items()
            if v is not None or k in {"unset_direction", "unset_planned"}
        }
        return await self._request("PUT", f"/tasks/{task_id}", json=clean)

    async def transition_status(
        self,
        task_id: int,
        *,
        to: str,
        changed_by: int | None = None,
        reason: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {"to": to}
        if changed_by is not None:
            body["changed_by"] = changed_by
        if reason:
            body["reason"] = reason
        return await self._request("PATCH", f"/tasks/{task_id}/status", json=body)

    async def delete(self, task_id: int) -> None:
        await self._request("DELETE", f"/tasks/{task_id}")

    async def add_favorite(self, task_id: int, user_id: int) -> dict:
        return await self._request(
            "POST", f"/tasks/{task_id}/favorite", json={"user_id": user_id}
        )

    async def remove_favorite(self, task_id: int, user_id: int) -> dict:
        return await self._request(
            "DELETE", f"/tasks/{task_id}/favorite", json={"user_id": user_id}
        )
