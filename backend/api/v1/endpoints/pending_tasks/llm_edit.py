"""
POST /api/v1/pending-tasks/{id}/llm-edit — естественный язык изменяет draft.

## Трассируемость
Feature: F017
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.pending_task_schema import PendingTaskResponseSchema
from service.chats.pending_task_service import PendingTaskService
from service.extractor.extractor_service import ExtractorService


router = APIRouter()
_pending_service = PendingTaskService()
_extractor = ExtractorService()


class LLMEditSchema(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=2000)


@router.post("/{pending_id}/llm-edit", response_model=PendingTaskResponseSchema)
async def llm_edit_pending(
    pending_id: int,
    data: LLMEditSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> PendingTaskResponseSchema:
    obj = await _pending_service.get_or_404(session, pending_id)
    current = {
        "title": (obj.draft or {}).get("title"),
        "description": (obj.draft or {}).get("description"),
        "deadline": (obj.draft or {}).get("deadline"),
        "priority": (obj.draft or {}).get("priority") or "medium",
    }
    updated = await _extractor.apply_edit(current, data.instruction)
    obj = await _pending_service.update_draft(session, pending_id, draft=updated)
    return PendingTaskResponseSchema.model_validate(obj)
