"""
VoiceAPI.

## Трассируемость
Feature: F002
Scenarios: SC004, SC005
"""

from __future__ import annotations

import httpx

from core.config import config


class VoiceAPI:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or config.backend_base).rstrip("/")

    async def transcribe(self, *, audio_bytes: bytes, file_name: str = "voice.ogg") -> str:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=60.0) as client:
            resp = await client.post(
                "/voice/transcribe",
                files={"file": (file_name, audio_bytes, "audio/ogg")},
            )
        resp.raise_for_status()
        return resp.json().get("text", "")
