"""Preference learning utilities"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.travel_plan import TravelPlan


@dataclass(slots=True)
class PreferenceLearningResult:
    """Aggregated preference insights derived from travel history"""

    default_budget_min: int | None = None
    default_budget_max: int | None = None
    last_budget_total: int | None = None
    preferred_traveler_types: list[str] = field(default_factory=list)
    preferred_interests: list[str] = field(default_factory=list)
    avoided_activities: list[str] = field(default_factory=list)
    dietary_restrictions: list[str] = field(default_factory=list)
    preferred_accommodation_type: list[str] = field(default_factory=list)
    preferred_pace: str | None = None
    recent_notes: str | None = None

    def has_history(self) -> bool:
        """Return True when any meaningful preference data exists"""

        return any(
            [
                self.default_budget_min is not None,
                self.default_budget_max is not None,
                self.last_budget_total is not None,
                bool(self.preferred_traveler_types),
                bool(self.preferred_interests),
                bool(self.avoided_activities),
                bool(self.dietary_restrictions),
                bool(self.preferred_accommodation_type),
                bool(self.preferred_pace),
                bool(self.recent_notes),
            ]
        )


class PreferenceLearningService:
    """Analyse user travel plans to derive reusable preferences"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def summarize_user_preferences(self, user_id: UUID) -> PreferenceLearningResult:
        """Collect aggregated insights from a user's historical travel plans"""

        result = await self.session.execute(
            select(TravelPlan)
            .where(TravelPlan.user_id == user_id)
            .order_by(TravelPlan.created_at.desc())
        )
        plans = list(result.scalars().all())
        if not plans:
            return PreferenceLearningResult()

        budgets = [plan.budget_total for plan in plans if plan.budget_total]
        traveler_counter: Counter[str] = Counter()
        interests_counter: Counter[str] = Counter()
        avoid_counter: Counter[str] = Counter()
        dietary_counter: Counter[str] = Counter()
        accommodation_counter: Counter[str] = Counter()

        last_notes: str | None = None
        last_pace: str | None = None

        for index, plan in enumerate(plans):
            if plan.traveler_type:
                traveler_counter.update([plan.traveler_type])

            pref_payload: dict[str, Any] = plan.preferences or {}
            request = pref_payload.get("request")
            if isinstance(request, dict):
                self._update_counter_from_iterable(
                    interests_counter, request.get("interests")
                )
                self._update_counter_from_iterable(
                    avoid_counter, request.get("avoid")
                )
                self._update_counter_from_iterable(
                    dietary_counter, request.get("dietary_restrictions")
                )
                request_notes = request.get("notes")
                request_pace = request.get("pace")
                if index == 0:
                    # 가장 최근 일정의 메모/페이스를 보관
                    last_notes = request_notes if isinstance(request_notes, str) else None
                    last_pace = request_pace if isinstance(request_pace, str) else None

            analysis = pref_payload.get("analysis")
            if isinstance(analysis, dict):
                self._update_counter_from_iterable(
                    accommodation_counter, analysis.get("themes")
                )

        summary = PreferenceLearningResult(
            default_budget_min=min(budgets) if budgets else None,
            default_budget_max=max(budgets) if budgets else None,
            last_budget_total=plans[0].budget_total if plans[0].budget_total else None,
            preferred_traveler_types=self._sorted_keys(traveler_counter),
            preferred_interests=self._sorted_keys(interests_counter),
            avoided_activities=self._sorted_keys(avoid_counter),
            dietary_restrictions=self._sorted_keys(dietary_counter),
            preferred_accommodation_type=self._sorted_keys(accommodation_counter),
            preferred_pace=last_pace,
            recent_notes=last_notes,
        )
        return summary

    @staticmethod
    def _sorted_keys(counter: Counter[str]) -> list[str]:
        return [item for item, _ in counter.most_common() if item]

    @staticmethod
    def _update_counter_from_iterable(counter: Counter[str], values: Any) -> None:
        if not isinstance(values, list):
            return
        normalized: list[str] = []
        for value in values:
            if isinstance(value, str) and value:
                normalized.append(value.strip())
        counter.update(normalized)
