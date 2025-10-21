"""Automatically maintain user preference records"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user_preference import UserPreference
from .learning import PreferenceLearningResult, PreferenceLearningService


class PreferenceAutoUpdater:
    """Persist learned preferences whenever travel plans are generated"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.learning_service = PreferenceLearningService(session)

    async def sync_from_history(self, user_id: UUID) -> UserPreference | None:
        """Recalculate and persist preference fields based on travel history"""

        summary = await self.learning_service.summarize_user_preferences(user_id)
        if not summary.has_history():
            return await self._get_existing(user_id)

        preference = await self._get_or_create(user_id)
        self._apply_summary(preference, summary)
        await self.session.flush()
        return preference

    async def _get_existing(self, user_id: UUID) -> UserPreference | None:
        result = await self.session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_or_create(self, user_id: UUID) -> UserPreference:
        existing = await self._get_existing(user_id)
        if existing:
            return existing

        preference = UserPreference(user_id=user_id)
        self.session.add(preference)
        await self.session.flush()
        return preference

    def _apply_summary(self, preference: UserPreference, summary: PreferenceLearningResult) -> None:
        if summary.default_budget_min is not None:
            preference.default_budget_min = summary.default_budget_min
        if summary.default_budget_max is not None:
            preference.default_budget_max = summary.default_budget_max

        if summary.preferred_traveler_types:
            preference.preferred_traveler_types = self._merge_lists(
                preference.preferred_traveler_types, summary.preferred_traveler_types
            )
        if summary.preferred_interests:
            preference.preferred_interests = self._merge_lists(
                preference.preferred_interests, summary.preferred_interests
            )
        if summary.avoided_activities:
            preference.avoided_activities = self._merge_lists(
                preference.avoided_activities, summary.avoided_activities
            )
        if summary.dietary_restrictions:
            preference.dietary_restrictions = self._merge_lists(
                preference.dietary_restrictions, summary.dietary_restrictions
            )
        if summary.preferred_accommodation_type:
            preference.preferred_accommodation_type = self._merge_lists(
                preference.preferred_accommodation_type, summary.preferred_accommodation_type
            )

    @staticmethod
    def _merge_lists(existing: list[str] | None, updates: list[str]) -> list[str]:
        merged: list[str] = []
        for value in updates + (existing or []):
            if value and value not in merged:
                merged.append(value)
        return merged
