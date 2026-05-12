"""
## Трассируемость
Feature: F005
Scenarios: SC012, SC013
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import db_connect
from schema.chats.message_ingest_schema import (
    MessageIngestResultSchema,
    MessageIngestSchema,
)
from service.chats.message_ingest_service import MessageIngestService


router = APIRouter()
_service = MessageIngestService()


@router.post("/ingest", response_model=MessageIngestResultSchema)
async def ingest_message(
    data: MessageIngestSchema,
    session: AsyncSession = Depends(db_connect.get_session),
) -> MessageIngestResultSchema:
    return await _service.ingest(session, data)
