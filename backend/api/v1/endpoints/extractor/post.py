"""
## Трассируемость
Feature: F001, F005
Scenarios: SC001, SC002, SC012, SC013
"""

from __future__ import annotations

from fastapi import APIRouter

from schema.extractor.extract_schema import ExtractRequestSchema, ExtractResponseSchema
from service.extractor.extractor_service import ExtractorService


router = APIRouter()
_service = ExtractorService()


@router.post("/", response_model=ExtractResponseSchema)
async def extract(data: ExtractRequestSchema) -> ExtractResponseSchema:
    classification = await _service.classify_message(
        data.text,
        context_messages=[m.model_dump() for m in data.context_messages],
    )
    deadline = classification.get("deadline")
    if deadline is None:
        deadline = await _service.parse_deadline(data.text, now=data.now)
    return ExtractResponseSchema(
        is_task=bool(classification.get("is_task")),
        title=classification.get("title"),
        deadline=deadline,
        confidence=float(classification.get("confidence") or 0.0),
        rationale=classification.get("rationale"),
    )
