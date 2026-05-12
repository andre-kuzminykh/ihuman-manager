"""
## Трассируемость
Feature: F007
Scenarios: SC018, SC019
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from schema.tasks.task_schema import TaskListItemSchema


class DigestGroupSchema(BaseModel):
    label: str
    tasks: list[TaskListItemSchema]


class DigestResponseSchema(BaseModel):
    user_id: int
    date: date
    is_empty: bool
    groups: list[DigestGroupSchema]
    total: int
