"""
## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from schema.voice.voice_schema import VoiceTranscribeResponseSchema
from service.voice.voice_service import VoiceService


router = APIRouter()
_service = VoiceService()


@router.post("/transcribe", response_model=VoiceTranscribeResponseSchema)
async def transcribe(file: UploadFile = File(...)) -> VoiceTranscribeResponseSchema:
    raw = await file.read()
    text = await _service.transcribe(audio_bytes=raw, file_name=file.filename or "voice.ogg")
    return VoiceTranscribeResponseSchema(text=text)
