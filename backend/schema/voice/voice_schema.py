"""
## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

from pydantic import BaseModel


class VoiceTranscribeResponseSchema(BaseModel):
    text: str
    duration_sec: float = 0.0
