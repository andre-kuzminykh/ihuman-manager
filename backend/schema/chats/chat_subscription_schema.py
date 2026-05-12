"""
## Трассируемость
Feature: F005
Scenarios: SC011
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatSubscriptionCreateSchema(BaseModel):
    chat_id: int
    owner_user_id: int
    title: str | None = None


class ChatSubscriptionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    owner_user_id: int
    title: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime
