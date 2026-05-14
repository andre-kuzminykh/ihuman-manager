"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC014
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PendingTaskUpdateSchema(BaseModel):
    draft: dict[str, Any] | None = None
    title: str | None = None
    text: str | None = None
    deadline: datetime | None = None
    direction_id: int | None = None


class PendingTaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    message_id: int
    owner_user_id: int
    source_text: str
    source_sender: str | None
    source_sender_display: str | None = None
    source_chat_username: str | None = None
    draft: dict[str, Any]
    is_auto_approved: bool
    approved: bool
    approved_at: datetime | None
    rejected_at: datetime | None
    created_task_id: int | None
    created_at: datetime
    updated_at: datetime
