"""
Pydantic-схемы направлений.

## Трассируемость
Feature: F009
Scenarios: SC022, SC023, SC024
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DirectionCreateSchema(BaseModel):
    user_id: int
    name: str = Field(..., min_length=1, max_length=80)
    is_favorite: bool = False

    @field_validator("name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("name must not be empty")
        return v2


class DirectionUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=80)
    is_favorite: bool | None = None


class DirectionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
