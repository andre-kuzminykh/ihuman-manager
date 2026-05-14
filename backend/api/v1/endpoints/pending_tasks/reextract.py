"""
POST /api/v1/pending-tasks/{id}/reextract — перегнать source_text заново
через текущий промт декомпозера. Заменяет draft pending'а.

## Трассируемость
Feature: F005 (доработка) + F019
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.pending_task_schema import PendingTaskResponseSchema
from service.chats.pending_task_service import PendingTaskService
from service.extractor.extractor_service import ExtractorService


router = APIRouter()
_pending = PendingTaskService()
_extractor = ExtractorService()


@router.post("/{pending_id}/reextract", response_model=PendingTaskResponseSchema)
async def reextract_pending(
    pending_id: int,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _pending.get_or_404(session, pending_id)
    extracted = await _extractor.extract_multiple(obj.source_text)
    if not extracted:
        return PendingTaskResponseSchema.model_validate(obj)
    first = extracted[0]
    deadline = first.get("deadline")
    draft = {
        "title": first.get("title"),
        "description": first.get("description"),
        "text": first.get("text") or first.get("title"),
        "deadline": deadline.isoformat() if isinstance(deadline, datetime) else deadline,
        "priority": first.get("priority") or "medium",
        "confidence": first.get("confidence"),
    }
    obj = await _pending.update_draft(session, pending_id, draft=draft)
    return PendingTaskResponseSchema.model_validate(obj)
