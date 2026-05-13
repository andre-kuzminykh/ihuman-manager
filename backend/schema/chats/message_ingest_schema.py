"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MessageIngestSchema(BaseModel):
    chat_id: int
    message_id: int
    sender_user_id: int | None = None
    sender_username: str | None = None
    text: str
    sent_at: datetime
    is_bot_mentioned: bool = False


class MessageIngestResultSchema(BaseModel):
    decision: Literal[
        "ignored",
        "pending_created",
        "pending_created_multi",
        "auto_approved",
        "auto_approved_multi",
        "duplicate",
        "not_subscribed",
    ]
    pending_task_id: int | None = None
    pending_task_ids: list[int] = []
    task_id: int | None = None
    task_ids: list[int] = []
    detail: str | None = None
