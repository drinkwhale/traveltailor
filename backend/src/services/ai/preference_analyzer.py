"""Preference analysis helpers"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...models.user_preference import UserPreference
from ...schemas.travel_plan import TravelPlanCreate, TravelPreferences


@dataclass
class AnalyzedPreferences:
    """Normalized preference bundle used by the planner"""

    interests: list[str]
    pace: str
    dietary_restrictions: list[str]
    traveler_persona: str
    themes: list[str]
    focus_budget: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "interests": self.interests,
            "pace": self.pace,
            "dietary_restrictions": self.dietary_restrictions,
            "traveler_persona": self.traveler_persona,
            "themes": self.themes,
            "focus_budget": self.focus_budget,
        }


class PreferenceAnalyzer:
    """Merge stored user preferences with the current request"""

    @staticmethod
    def _merge_lists(*values: list[str]) -> list[str]:
        merged: list[str] = []
        for value in values:
            for item in value:
                if item and item not in merged:
                    merged.append(item)
        return merged

    def analyze(
        self,
        request: TravelPlanCreate,
        stored: UserPreference | None = None,
    ) -> AnalyzedPreferences:
        req_prefs: TravelPreferences = request.preferences

        interests = self._merge_lists(
            stored.preferred_interests if stored and stored.preferred_interests else [],
            req_prefs.interests,
        ) or ["culture", "food"]

        dietary = self._merge_lists(
            stored.dietary_restrictions if stored and stored.dietary_restrictions else [],
            req_prefs.dietary_restrictions,
        )

        persona = request.traveler_type
        if stored and stored.preferred_traveler_types:
            if request.traveler_type not in stored.preferred_traveler_types:
                persona = stored.preferred_traveler_types[0]

        themes = self._merge_lists(
            req_prefs.must_have,
            stored.preferred_interests if stored and stored.preferred_interests else [],
        )
        if req_prefs.notes:
            themes.append("notes: " + req_prefs.notes)

        focus_budget = "moderate"
        if stored and stored.default_budget_max:
            avg_budget = (stored.default_budget_min or 0 + stored.default_budget_max) / 2
            if avg_budget < 500000:
                focus_budget = "budget"
            elif avg_budget > 1500000:
                focus_budget = "premium"

        if request.budget_total < 500000:
            focus_budget = "budget"
        elif request.budget_total > 2000000:
            focus_budget = "premium"

        return AnalyzedPreferences(
            interests=interests,
            pace=req_prefs.pace,
            dietary_restrictions=dietary,
            traveler_persona=persona,
            themes=themes,
            focus_budget=focus_budget,
        )

