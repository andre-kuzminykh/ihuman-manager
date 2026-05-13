"""
POST /api/v1/extract/multi — извлечение нескольких задач.

## Трассируемость
Feature: F015
Scenarios: SC033, SC034
"""

from __future__ import annotations

from fastapi import APIRouter

from schema.extractor.extract_schema import (
    ExtractMultiResponseSchema,
    ExtractRequestSchema,
    ExtractedTaskSchema,
)
from service.extractor.extractor_service import ExtractorService


router = APIRouter()
_service = ExtractorService()


@router.post("/multi", response_model=ExtractMultiResponseSchema)
async def extract_multi(data: ExtractRequestSchema) -> ExtractMultiResponseSchema:
    extracted = await _service.extract_multiple(
        data.text,
        context_messages=[m.model_dump() for m in data.context_messages],
    )
    tasks = [
        ExtractedTaskSchema(
            title=item["title"],
            text=item["text"],
            deadline=item.get("deadline"),
            confidence=float(item.get("confidence") or 0.0),
        )
        for item in extracted
    ]
    return ExtractMultiResponseSchema(tasks=tasks)
