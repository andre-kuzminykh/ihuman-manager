"""
## Трассируемость
Feature: F020
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonTouchSchema(BaseModel):
    telegram_user_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_bot: bool = False
    language_code: str | None = None
    is_premium: bool = False


class PersonResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_user_id: int | None
    username: str | None
    first_name: str | None
    last_name: str | None
    is_bot: bool
    language_code: str | None
    is_premium: bool
    last_seen_at: datetime | None
    message_count: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
