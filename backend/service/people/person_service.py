"""
PersonService — upsert/touch контактов.

## Трассируемость
Feature: F020
Scenarios: SC040, SC041
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from model.people.person_model import PersonModel
from repository.people.person_repository import PersonRepository
from service.utils.time_utils import now_msk


class PersonService:
    def __init__(self, repo: PersonRepository | None = None) -> None:
        self._repo = repo or PersonRepository()

    async def touch(
        self,
        session: AsyncSession,
        *,
        telegram_user_id: int | None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_bot: bool = False,
        language_code: str | None = None,
        is_premium: bool = False,
    ) -> PersonModel | None:
        """Идемпотентный upsert: создать или обновить контакт.
        Если telegram_user_id=None — пытаемся найти по username; если ничего нет — ничего не делаем.
        Инкрементит message_count и обновляет last_seen_at.
        """
        person: PersonModel | None = None
        if telegram_user_id is not None:
            person = await self._repo.get_by_telegram_id(session, telegram_user_id)
        elif username:
            person = await self._repo.find_by_username(session, username)
        else:
            return None

        if person is None:
            person = await self._repo.create(
                session,
                telegram_user_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_bot=is_bot,
                language_code=language_code,
                is_premium=is_premium,
                last_seen_at=now_msk(),
                message_count=1,
            )
            return person

        # update fields that могли поменяться
        if username and person.username != username:
            person.username = username
        if first_name and person.first_name != first_name:
            person.first_name = first_name
        if last_name and person.last_name != last_name:
            person.last_name = last_name
        if language_code and person.language_code != language_code:
            person.language_code = language_code
        if is_premium and not person.is_premium:
            person.is_premium = is_premium
        person.last_seen_at = now_msk()
        person.message_count = (person.message_count or 0) + 1
        await session.flush()
        await session.refresh(person)
        return person

    async def list_all(self, session: AsyncSession) -> list[PersonModel]:
        return await self._repo.list_all(session)
