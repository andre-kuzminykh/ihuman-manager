"""
Pydantic-схемы задачи.

## Трассируемость
Feature: F001, F002, F003, F004, F008, F009
Scenarios: SC001–SC010, SC020, SC021
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from model.enums import TaskPriority, TaskSource, TaskStatus


class TaskCreateSchema(BaseModel):
    user_id: int
    text: str = Field(..., min_length=1, max_length=5000)
    chat_id: int | None = None
    source_message_id: int | None = None
    source_kind: TaskSource = TaskSource.TEXT
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    direction_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    force: bool = False  # пропустить дедуп (F010 BR031)

    @field_validator("text")
    @classmethod
    def _strip_text(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("text must not be empty")
        return v2


class TaskUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    text: str | None = Field(None, min_length=1, max_length=5000)
    description: str | None = None
    deadline: datetime | None = None
    direction_id: int | None = None
    priority: TaskPriority | None = None
    planned_start_at: datetime | None = None
    planned_end_at: datetime | None = None
    # sentinel "unset" — отличаем "не передавать" от "сбросить в null"
    unset_direction: bool = False
    unset_planned: bool = False
    unset_description: bool = False


class TaskStatusUpdateSchema(BaseModel):
    to: TaskStatus
    reason: str | None = None
    changed_by: int | None = None


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    chat_id: int | None
    source_message_id: int | None = None
    title: str
    text: str
    description: str | None = None
    status: TaskStatus
    source_kind: TaskSource
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: datetime
    planned_start_at: datetime | None
    planned_end_at: datetime | None
    direction_id: int | None
    is_favorite: bool = False
    is_duplicate: bool = False  # F010 — задача уже существовала
    paused_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskListItemSchema(TaskResponseSchema):
    pass
