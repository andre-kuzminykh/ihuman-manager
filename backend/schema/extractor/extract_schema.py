"""
## Трассируемость
Feature: F001, F005
Scenarios: SC001, SC012
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ContextMessageSchema(BaseModel):
    sender_username: str | None = None
    text: str
    sent_at: datetime | None = None


class ExtractRequestSchema(BaseModel):
    text: str
    now: datetime | None = None
    context_messages: list[ContextMessageSchema] = []


class ExtractResponseSchema(BaseModel):
    is_task: bool
    title: str | None
    deadline: datetime | None
    confidence: float = 0.0
    rationale: str | None = None
