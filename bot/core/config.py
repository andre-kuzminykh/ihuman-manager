"""
core.config — настройки бота.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "hmnd_taskbot"
    BOT_OWNER_USERNAME: str = ""

    BACKEND_URL: str = "http://localhost:8000"
    BACKEND_API_PREFIX: str = "/api/v1"

    MEDIA_DIR: Path = Path("./data/media")
    LOG_LEVEL: str = "INFO"

    BOT_SCHEDULER_TICK_SECONDS: int = 300

    @property
    def backend_base(self) -> str:
        return f"{self.BACKEND_URL.rstrip('/')}{self.BACKEND_API_PREFIX}"


config = Settings()
