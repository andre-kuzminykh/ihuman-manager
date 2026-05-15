"""
POST /api/v1/tasks/batch — извлечь и создать несколько задач за один вызов.

## Трассируемость
Feature: F015
Scenarios: SC033, SC034
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from model.enums import TaskSource
from service.extractor.extractor_service import ExtractorService
from service.tasks.task_service import TaskService


router = APIRouter()
_task_service = TaskService()
_extractor = ExtractorService()


class BatchCreateSchema(BaseModel):
    user_id: int
    text: str = Field(..., min_length=1, max_length=10000)
    chat_id: int | None = None
    source_message_id: int | None = None
    source_sender_user_id: int | None = None
    source_sender_username: str | None = None
    source_sender_display: str | None = None
    source_chat_username: str | None = None
    source_kind: TaskSource = TaskSource.TEXT
    force: bool = False
    context_messages: list[dict] = []

    @field_validator("text")
    @classmethod
    def _strip(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v.strip()


@router.post("/batch")
async def create_batch(
    data: BatchCreateSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> dict[str, Any]:
    extracted = await _extractor.extract_multiple(
        data.text, context_messages=data.context_messages
    )
    results = await _task_service.create_many_from_extraction(
        session,
        user_id=data.user_id,
        extracted=extracted,
        chat_id=data.chat_id,
        source_message_id=data.source_message_id,
        source_sender_user_id=data.source_sender_user_id,
        source_sender_username=data.source_sender_username,
        source_sender_display=data.source_sender_display,
        source_chat_username=data.source_chat_username,
        source_kind=data.source_kind,
        force=data.force,
    )
    tasks_payload = []
    duplicates = 0
    for task, is_dup in results:
        payload = await _task_service.to_response(session, task)
        payload["is_duplicate"] = is_dup
        if is_dup:
            duplicates += 1
        tasks_payload.append(payload)
    return {
        "count": len(tasks_payload),
        "duplicates": duplicates,
        "tasks": tasks_payload,
    }
