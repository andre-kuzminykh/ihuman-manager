"""
core.config — типизированные настройки сервиса.

Все переменные читаются из окружения. Дефолты подходят для локального dev.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # DB
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "ihuman_manager"

    # LLM
    OPENAI_API_KEY: str = ""
    # Двухступенчатый pipeline:
    #  1) CLASSIFIER_MODEL — быстрый/дешёвый: «есть ли вообще задачи?»
    #  2) DECOMPOSER_MODEL — мощный: декомпозиция в структурированный список
    # LLM_MODEL остаётся для совместимости (используется в apply_edit и т.п.)
    LLM_MODEL: str = "gpt-4o-mini"
    CLASSIFIER_MODEL: str = "gpt-4o-mini"
    DECOMPOSER_MODEL: str = "gpt-5.4"
    WHISPER_MODEL: str = "gpt-4o-transcribe"

    # Scheduler
    SCHEDULER_TICK_SECONDS: int = 300
    MORNING_DIGEST_HOUR_MSK: int = 9
    DEFAULT_DEADLINE_HOUR_MSK: int = 18

    # Misc
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"
    DEFAULT_TASK_DURATION_MINUTES: int = 30
    DEADLINE_TODO_WINDOW_DAYS: int = 7
    MAX_CONTEXT_MESSAGES: int = 20

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


config = Settings()
