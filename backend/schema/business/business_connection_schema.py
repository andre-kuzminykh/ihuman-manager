"""
## Трассируемость
Feature: F018
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BusinessConnectionCreateSchema(BaseModel):
    business_connection_id: str
    owner_user_id: int
    is_enabled: bool = True
    can_reply: bool = False


class BusinessConnectionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_connection_id: str
    owner_user_id: int
    is_enabled: bool
    can_reply: bool
    created_at: datetime
    updated_at: datetime
