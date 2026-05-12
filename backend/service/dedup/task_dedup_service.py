"""
TaskDedupService — поиск похожих активных задач.

## Трассируемость
Feature: F010
Scenarios: SC025, SC026, SC027 (BR027–BR031)

## Алгоритм
1. Нормализация: lower → удалить пунктуацию → схлопнуть whitespace.
2. Topic-prefix: первое слово длиной ≥3 нормализованного title должно совпасть.
3. Если есть — считаем rapidfuzz.token_set_ratio. ≥ порога → дубль.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from model.enums import TaskStatus
from model.tasks.task_model import TaskModel
from repository.tasks.task_repository import TaskRepository
from service.utils.time_utils import now_msk


_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+", re.UNICODE)

_ACTIVE_STATUSES: tuple[TaskStatus, ...] = (
    TaskStatus.BACKLOG,
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.PAUSED,
    TaskStatus.BLOCKED,
)


def normalize(text: str) -> str:
    if not text:
        return ""
    s = text.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def topic_prefix(text: str, *, min_len: int = 3) -> str:
    norm = normalize(text)
    for word in norm.split(" "):
        if len(word) >= min_len:
            return word
    return ""


class TaskDedupService:
    def __init__(
        self,
        task_repo: TaskRepository | None = None,
        *,
        threshold: int = 85,
        window_days: int = 7,
    ) -> None:
        self._task_repo = task_repo or TaskRepository()
        self._threshold = threshold
        self._window_days = window_days

    async def find_duplicate(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        title: str,
        active_statuses: Iterable[TaskStatus] = _ACTIVE_STATUSES,
        now: datetime | None = None,
    ) -> TaskModel | None:
        norm_title = normalize(title)
        if not norm_title:
            return None
        prefix = topic_prefix(title)
        if not prefix:
            return None

        from rapidfuzz import fuzz

        n = now or now_msk()
        # окно — задачи, обновлённые/созданные за последние N дней
        cutoff = n - timedelta(days=self._window_days)

        candidates = await self._task_repo.list_for_user(
            session,
            user_id,
            statuses=active_statuses,
            deadline_after=cutoff,
        )
        # включаем и более старые активные — обрезку по cutoff делает только deadline_after,
        # ниже сравниваем по created_at, чтобы окно работало для бэклога
        all_active = await self._task_repo.list_for_user(
            session, user_id, statuses=active_statuses
        )
        seen = {t.id for t in candidates}
        for t in all_active:
            if t.id in seen:
                continue
            if t.created_at >= cutoff:
                candidates.append(t)
                seen.add(t.id)

        best: tuple[int, TaskModel] | None = None
        for task in candidates:
            existing_norm = normalize(task.title)
            if not existing_norm:
                continue
            if topic_prefix(task.title) != prefix:
                continue
            ratio = int(fuzz.token_set_ratio(norm_title, existing_norm))
            if ratio >= self._threshold and (best is None or ratio > best[0]):
                best = (ratio, task)
        return best[1] if best else None
