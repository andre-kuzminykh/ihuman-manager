"""
conftest.py — глобальные фикстуры для бэкенд-тестов.

Поднимает временную тестовую БД (PostgreSQL по умолчанию, sqlite fallback
для CI без Postgres). Тип JSONB в PendingTaskModel заменяется на JSON для
SQLite (см. patch `_patch_json_for_sqlite`).
"""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core import app, db_connect
from model import Base


def _test_db_url() -> str:
    explicit = os.getenv("TEST_DATABASE_URL")
    if explicit:
        return explicit
    if os.getenv("USE_SQLITE_TESTS", "").lower() in {"1", "true", "yes"}:
        return "sqlite+aiosqlite:///:memory:"
    host = os.getenv("TEST_DB_HOST", os.getenv("DB_HOST", "localhost"))
    port = os.getenv("TEST_DB_PORT", os.getenv("DB_PORT", "5432"))
    user = os.getenv("TEST_DB_USER", os.getenv("DB_USER", "postgres"))
    password = os.getenv("TEST_DB_PASSWORD", os.getenv("DB_PASSWORD", "postgres"))
    name = os.getenv("TEST_DB_NAME", os.getenv("DB_NAME", "ihuman_manager_test"))
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


def _patch_json_for_sqlite(url: str) -> None:
    if not url.startswith("sqlite"):
        return
    from model.chats import pending_task_model

    pending_task_model.PendingTaskModel.__table__.c.draft.type = JSON()


@pytest_asyncio.fixture
async def async_session() -> AsyncSession:
    url = _test_db_url()
    _patch_json_for_sqlite(url)
    engine = create_async_engine(url, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(async_session: AsyncSession) -> AsyncClient:
    async def override():
        try:
            yield async_session
            await async_session.commit()
        except Exception:
            await async_session.rollback()
            raise

    app.dependency_overrides[db_connect.get_session] = override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
