"""
Voice transcription endpoint.

## Трассируемость
Feature: F002
"""

from fastapi import APIRouter

from api.v1.endpoints.voice.post import router as post_router


router = APIRouter(prefix="/voice", tags=["voice"])
router.include_router(post_router)

__all__ = ["router"]
