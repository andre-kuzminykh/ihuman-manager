"""
ExtractorService — извлечение задач и парсинг дедлайнов.

## Трассируемость
Feature: F001 (BR001, BR003), F005 (BR014)
Scenarios: SC001, SC002, SC012, SC013

## Дизайн
- parse_deadline / build_title — детерминированные эвристики (без LLM), работают офлайн.
- classify / extract — оборачивают OpenAI, при отсутствии API_KEY используют heuristic-фоллбек.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Sequence

from dateutil import parser as dateparser

from core.config import config
from service.utils.time_utils import MSK, now_msk, today_msk_default_deadline


log = logging.getLogger(__name__)


_WEEKDAYS = {
    "понедельник": 0, "пн": 0,
    "вторник": 1, "вт": 1,
    "среда": 2, "ср": 2, "среду": 2,
    "четверг": 3, "чт": 3,
    "пятница": 4, "пт": 4, "пятницу": 4,
    "суббота": 5, "сб": 5, "субботу": 5,
    "воскресенье": 6, "вс": 6,
}

_REL_DAYS = {
    "сегодня": 0,
    "завтра": 1,
    "послезавтра": 2,
}

_TIME_RE = re.compile(r"\b(?P<h>\d{1,2})[:.](?P<m>\d{2})\b")
_DATE_RE = re.compile(r"\b(?P<d>\d{1,2})\.(?P<mo>\d{1,2})(?:\.(?P<y>\d{2,4}))?\b")


class ExtractorService:
    """Двухступенчатый pipeline:
       1) classifier (CLASSIFIER_MODEL, дёшево) — есть ли вообще задача?
       2) decomposer (DECOMPOSER_MODEL, мощно) — структурированный список задач.
    LLM_MODEL остаётся для apply_edit и classify_message (legacy).
    """

    def __init__(
        self,
        openai_api_key: str | None = None,
        llm_model: str | None = None,
        classifier_model: str | None = None,
        decomposer_model: str | None = None,
    ) -> None:
        self._api_key = openai_api_key if openai_api_key is not None else config.OPENAI_API_KEY
        self._model = llm_model or config.LLM_MODEL
        self._classifier_model = classifier_model or config.CLASSIFIER_MODEL
        self._decomposer_model = decomposer_model or config.DECOMPOSER_MODEL
        self._client = None
        if self._api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self._api_key)
            except Exception as exc:  # pragma: no cover - import-time
                log.warning("OpenAI SDK init failed: %s", exc)
                self._client = None

    # ---------- deterministic helpers ----------

    def build_title(self, text: str) -> str:
        cleaned = (text or "").strip()
        if "." in cleaned:
            cleaned = cleaned.split(".", 1)[0]
        return cleaned[:120].strip()

    async def parse_deadline(
        self, text: str, *, now: datetime | None = None
    ) -> datetime | None:
        """Возвращает дедлайн в зоне MSK или None, если не получилось распознать."""
        if not text:
            return None
        n = (now or now_msk()).astimezone(MSK)
        text_lower = text.lower()

        # 1) "сегодня", "завтра", "послезавтра"
        rel_day_match: tuple[int, str] | None = None
        for word, delta in _REL_DAYS.items():
            if re.search(rf"\b{word}\b", text_lower):
                rel_day_match = (delta, word)
                break

        # 2) "в пятницу", "до пятницы"
        weekday_match: int | None = None
        for word, idx in _WEEKDAYS.items():
            if re.search(rf"\b(?:в|до|к)\s+{word}\b", text_lower):
                weekday_match = idx
                break

        # 3) "12.05" / "12.05.2026"
        date_match: datetime | None = None
        m = _DATE_RE.search(text_lower)
        if m:
            try:
                day = int(m.group("d"))
                month = int(m.group("mo"))
                year = int(m.group("y")) if m.group("y") else n.year
                if year < 100:
                    year += 2000
                date_match = MSK.localize(datetime(year, month, day))
            except ValueError:
                date_match = None

        # 4) "HH:MM"
        time_part: tuple[int, int] | None = None
        tm = _TIME_RE.search(text_lower)
        if tm:
            try:
                hh, mm = int(tm.group("h")), int(tm.group("m"))
                if 0 <= hh < 24 and 0 <= mm < 60:
                    time_part = (hh, mm)
            except ValueError:
                time_part = None

        target: datetime | None = None
        if date_match is not None:
            target = date_match
        elif weekday_match is not None:
            days_ahead = (weekday_match - n.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = (n + timedelta(days=days_ahead)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif rel_day_match is not None:
            target = (n + timedelta(days=rel_day_match[0])).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        if target is None:
            try:
                parsed = dateparser.parse(
                    text,
                    dayfirst=True,
                    fuzzy=True,
                    default=n,
                )
                if parsed is not None and abs((parsed - n).days) < 365:
                    target = MSK.localize(parsed.replace(tzinfo=None)) if parsed.tzinfo is None else parsed.astimezone(MSK)
            except (ValueError, OverflowError):
                target = None

        if target is None:
            return None

        if time_part is not None:
            target = target.replace(hour=time_part[0], minute=time_part[1], second=0, microsecond=0)
        else:
            target = target.replace(
                hour=config.DEFAULT_DEADLINE_HOUR_MSK, minute=0, second=0, microsecond=0
            )
        return target

    # ---------- LLM API ----------

    async def classify_message(
        self,
        text: str,
        *,
        context_messages: Sequence[dict] | None = None,
    ) -> dict:
        """Классифицирует одно сообщение в контексте 10 последних.

        Возвращает {is_task, title, deadline (iso|None), confidence, rationale}.

        Если LLM недоступен — heuristic: считаем задачей, если в тексте есть
        глаголы повеления (срочно/надо/подготовь/сделай и т.п.).
        """
        if self._client is None:
            return self._heuristic_classify(text)

        try:
            now_iso = now_msk().isoformat()
            context_text = "\n".join(
                f"{m.get('sender_username') or 'user'}: {m.get('text','')}"
                for m in (context_messages or [])
            )
            system_prompt = (
                "Ты — помощник-классификатор задач из чата. Получаешь сообщение и "
                "контекст из последних 10 сообщений. Ответ — строгий JSON со схемой:"
                ' {"is_task": bool, "title": str|null, "deadline": ISO8601|null,'
                ' "confidence": float (0..1), "rationale": str}. '
                f"Текущая дата (MSK): {now_iso}. Дедлайны интерпретируй в Europe/Moscow."
            )
            user_prompt = (
                f"Контекст:\n{context_text}\n\nСообщение:\n{text}\n\n"
                "Если в сообщении явное поручение/обещание/договорённость — is_task=true."
            )
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw = resp.choices[0].message.content or "{}"
            data = json.loads(raw)
            return self._normalize_llm_output(data)
        except Exception as exc:  # pragma: no cover - сетевой/parsing fallback
            log.warning("LLM classify failed: %s — fallback to heuristic", exc)
            return self._heuristic_classify(text)

    def _normalize_llm_output(self, data: dict) -> dict:
        deadline = data.get("deadline")
        deadline_dt: datetime | None = None
        if deadline:
            try:
                deadline_dt = dateparser.isoparse(deadline)
                if deadline_dt.tzinfo is None:
                    deadline_dt = MSK.localize(deadline_dt)
                else:
                    deadline_dt = deadline_dt.astimezone(MSK)
            except (ValueError, TypeError):
                deadline_dt = None
        return {
            "is_task": bool(data.get("is_task", False)),
            "title": (data.get("title") or "").strip() or None,
            "deadline": deadline_dt,
            "confidence": float(data.get("confidence") or 0.0),
            "rationale": data.get("rationale"),
        }

    def _heuristic_classify(self, text: str) -> dict:
        markers = (
            "надо",
            "нужно",
            "срочно",
            "подготовь",
            "подготовьте",
            "сделай",
            "сделайте",
            "отправь",
            "позвони",
            "напомни",
            "до завтра",
            "до пятницы",
            "до понедельника",
            "к понедельнику",
            "к пятнице",
            "task:",
        )
        low = (text or "").lower()
        is_task = any(m in low for m in markers)
        return {
            "is_task": is_task,
            "title": self.build_title(text) if is_task else None,
            "deadline": None,
            "confidence": 0.5 if is_task else 0.1,
            "rationale": "heuristic_fallback",
        }

    # ---------- multi-task ----------

    MAX_MULTI_TASKS = 10

    async def is_message_taskful(
        self,
        text: str,
        *,
        context_messages: list[dict] | None = None,
    ) -> bool:
        """Быстрый классификатор: есть ли в сообщении хотя бы одна задача?

        Использует CLASSIFIER_MODEL (дешёвая/быстрая). При отсутствии LLM —
        эвристика по словам-маркерам.

        ## Трассируемость
        Feature: F015, F019 (двухступенчатый pipeline)
        """
        if self._client is None:
            return self._heuristic_classify(text).get("is_task", False)
        try:
            context_text = "\n".join(
                f"{m.get('sender_username') or 'user'}: {m.get('text','')}"
                for m in (context_messages or [])
            )
            system = (
                "Ты — классификатор. Получаешь сообщение и контекст. Решаешь, "
                "содержит ли оно хотя бы одну задачу/поручение/обещание сделать "
                "что-то конкретное. Ответ — строгий JSON: "
                '{"has_task": bool, "reason": str}. '
                "has_task=true только если в сообщении есть осмысленное "
                "действие, у которого есть исполнитель (явный или подразумеваемый), "
                "и оно НЕ описывает уже свершившееся прошлое."
            )
            user = f"Контекст:\n{context_text}\n\nСообщение:\n{text}"
            log.info(
                "CLASSIFIER input: model=%s text=%r context=%r",
                self._classifier_model,
                text[:300],
                context_text[:600],
            )
            resp = await self._client.chat.completions.create(
                model=self._classifier_model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw = resp.choices[0].message.content or "{}"
            log.info("CLASSIFIER raw output: %s", raw)
            data = json.loads(raw)
            verdict = bool(data.get("has_task", False))
            log.info(
                "CLASSIFIER verdict: has_task=%s reason=%r",
                verdict,
                data.get("reason"),
            )
            return verdict
        except Exception as exc:  # pragma: no cover
            log.warning("LLM classifier failed: %s — heuristic", exc)
            return self._heuristic_classify(text).get("is_task", False)

    async def extract_multiple(
        self,
        text: str,
        *,
        context_messages: list[dict] | None = None,
    ) -> list[dict]:
        """Двухступенчатое извлечение задач.

        ## Трассируемость
        Feature: F015 (BR042–BR046), F019 (two-stage pipeline)
        Scenarios: SC033, SC034, SC035

        Pipeline:
          1) is_message_taskful (CLASSIFIER_MODEL) — фильтр пустого трепа.
          2) decomposer (DECOMPOSER_MODEL) — структурированный список задач.
        """
        if self._client is None:
            return self._heuristic_extract_multiple(text)

        # Stage 1: классификатор.
        taskful = await self.is_message_taskful(text, context_messages=context_messages)
        if not taskful:
            log.info("classifier: not taskful, skipping decomposer")
            return []

        try:
            now_iso = now_msk().isoformat()
            context_text = "\n".join(
                f"{m.get('sender_username') or 'user'}: {m.get('text','')}"
                for m in (context_messages or [])
            )
            system_prompt = (
                "Ты — экстрактор задач. Получаешь сообщение пользователя и контекст. "
                "Извлеки все самостоятельные задачи и верни строгий JSON: "
                '{"tasks":[{"title":str,"description":str|null,"text":str,'
                '"deadline":ISO8601|null,"priority":"low"|"medium"|"high",'
                '"confidence":float}, ...], "rationale":str}.\n'
                "Правила:\n"
                "- Каждая задача — отдельный пункт. Если действий несколько ('A и B'), "
                "это две задачи.\n"
                "- Если нет ни одной задачи — tasks: [].\n"
                "- title — короткий повелительный текст до 120 символов.\n"
                "- description — 1–2 предложения контекста (кто, что, зачем), берётся "
                "из исходного сообщения и контекста чата. Если контекст пустой — null.\n"
                "- deadline парси в Europe/Moscow; если не указан — null.\n"
                "- priority: high если есть слова 'срочно', 'asap', 'важно', "
                "'критично'; low если 'когда будет время', 'не горит'; иначе medium.\n"
                "- confidence ∈ [0,1].\n"
                f"Текущая дата (MSK): {now_iso}."
            )
            user_prompt = f"Контекст:\n{context_text}\n\nСообщение:\n{text}"
            log.info(
                "DECOMPOSER input: model=%s text=%r context=%r",
                self._decomposer_model,
                text[:300],
                context_text[:1200],
            )
            resp = await self._client.chat.completions.create(
                model=self._decomposer_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw = resp.choices[0].message.content or "{}"
            log.info("DECOMPOSER raw output: %s", raw[:2000])
            data = json.loads(raw)
            normalized = self._normalize_multi_output(data)
            log.info(
                "DECOMPOSER normalized %d tasks: %s",
                len(normalized),
                [{"title": t["title"], "priority": t.get("priority")} for t in normalized],
            )
            return normalized
        except Exception as exc:  # pragma: no cover
            log.warning("LLM extract_multiple failed: %s — heuristic fallback", exc)
            return self._heuristic_extract_multiple(text)

    def _normalize_multi_output(self, data: dict) -> list[dict]:
        raw_tasks = data.get("tasks") or []
        if not isinstance(raw_tasks, list):
            return []
        result: list[dict] = []
        for t in raw_tasks[: self.MAX_MULTI_TASKS]:
            if not isinstance(t, dict):
                continue
            title = (t.get("title") or "").strip()
            if not title:
                continue
            txt = (t.get("text") or title).strip()
            deadline_raw = t.get("deadline")
            deadline_dt: datetime | None = None
            if deadline_raw:
                try:
                    deadline_dt = dateparser.isoparse(deadline_raw)
                    deadline_dt = (
                        MSK.localize(deadline_dt)
                        if deadline_dt.tzinfo is None
                        else deadline_dt.astimezone(MSK)
                    )
                except (ValueError, TypeError):
                    deadline_dt = None
            prio = str(t.get("priority") or "medium").lower()
            if prio not in {"low", "medium", "high"}:
                prio = "medium"
            desc = (t.get("description") or "").strip() or None
            result.append(
                {
                    "title": title[:120],
                    "description": desc[:2000] if desc else None,
                    "text": txt[:5000],
                    "deadline": deadline_dt,
                    "priority": prio,
                    "confidence": float(t.get("confidence") or 0.0),
                }
            )
        return result

    def _heuristic_extract_multiple(self, text: str) -> list[dict]:
        """Эвристика без LLM — режем по союзам 'и', 'а ещё', ';', '\\n'."""
        single = self._heuristic_classify(text)
        if not single.get("is_task"):
            return []
        cleaned = (text or "").strip()
        # пробуем разбить по очевидным разделителям
        parts: list[str] = []
        for chunk in re.split(r"[\n;]| и | а ещё | потом ", cleaned, flags=re.IGNORECASE):
            chunk = chunk.strip(" .,!?")
            if len(chunk) >= 3:
                parts.append(chunk)
        if len(parts) <= 1:
            return [
                {
                    "title": self.build_title(cleaned),
                    "text": cleaned,
                    "deadline": None,
                    "confidence": 0.5,
                }
            ]
        return [
            {
                "title": self.build_title(p),
                "text": p,
                "deadline": None,
                "confidence": 0.4,
            }
            for p in parts[: self.MAX_MULTI_TASKS]
        ]

    # ---------- natural-language edit ----------

    EDITABLE_FIELDS = ("title", "description", "deadline", "priority")

    async def apply_edit(
        self,
        current: dict,
        instruction: str,
    ) -> dict:
        """Применить инструкцию к черновику задачи через LLM.

        ## Трассируемость
        Feature: F017 (LLM-edit, естественный язык)

        current — текущие поля: {title, description, deadline (iso|None), priority}.
        instruction — текст пользователя ('переименуй на ..., поставь deadline ...').
        Возвращает обновлённый dict (только изменённые поля + остальные as-is).
        """
        if self._client is None:
            return self._heuristic_apply_edit(current, instruction)
        try:
            now_iso = now_msk().isoformat()
            system = (
                "Ты — редактор черновика задачи. Получаешь текущие поля и инструкцию "
                "пользователя на естественном языке. Верни строгий JSON с тем же "
                "набором ключей (title, description, deadline (ISO8601|null), "
                "priority (low|medium|high)). Изменяй ТОЛЬКО те поля, что упомянул "
                "пользователь. Остальные оставь как есть. "
                f"Текущая дата (MSK): {now_iso}. Дедлайны в Europe/Moscow."
            )
            user = (
                f"Текущие поля JSON:\n{json.dumps(current, ensure_ascii=False)}\n\n"
                f"Инструкция: {instruction}"
            )
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw = resp.choices[0].message.content or "{}"
            data = json.loads(raw)
            return self._normalize_edit_output(current, data)
        except Exception as exc:  # pragma: no cover
            log.warning("LLM apply_edit failed: %s — heuristic", exc)
            return self._heuristic_apply_edit(current, instruction)

    def _normalize_edit_output(self, current: dict, data: dict) -> dict:
        out = dict(current)
        if "title" in data and isinstance(data["title"], str) and data["title"].strip():
            out["title"] = data["title"].strip()[:200]
        if "description" in data:
            desc = data["description"]
            if isinstance(desc, str):
                out["description"] = desc.strip()[:2000] or None
            elif desc is None:
                out["description"] = None
        if "deadline" in data:
            dl = data["deadline"]
            if isinstance(dl, str) and dl:
                try:
                    dt = dateparser.isoparse(dl)
                    dt = MSK.localize(dt) if dt.tzinfo is None else dt.astimezone(MSK)
                    out["deadline"] = dt.isoformat()
                except (ValueError, TypeError):
                    pass
            elif dl is None:
                out["deadline"] = None
        if "priority" in data:
            prio = str(data["priority"] or "").lower()
            if prio in {"low", "medium", "high"}:
                out["priority"] = prio
        return out

    def _heuristic_apply_edit(self, current: dict, instruction: str) -> dict:
        """Совсем грубо: ищем 'дедлайн ...', 'приоритет ...' в инструкции."""
        out = dict(current)
        low = (instruction or "").lower()
        if "высок" in low or "срочн" in low or "high" in low:
            out["priority"] = "high"
        elif "низк" in low or "не горит" in low or "low" in low:
            out["priority"] = "low"
        return out
