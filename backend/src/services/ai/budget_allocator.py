"""
Budget allocation utilities
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ...schemas.travel_plan import BudgetBreakdown
from .preference_analyzer import AnalyzedPreferences


@dataclass
class BudgetAllocationResult:
    """Value object for budget decomposition"""

    breakdown: BudgetBreakdown
    per_day: int
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, int | dict[str, int] | list[str]]:
        return {
            "breakdown": {
                "accommodation": self.breakdown.accommodation,
                "food": self.breakdown.food,
                "activities": self.breakdown.activities,
                "transport": self.breakdown.transport,
            },
            "per_day": self.per_day,
            "warnings": self.warnings,
        }


class BudgetAllocator:
    """Simple heuristic budget allocator based on traveler persona"""

    BASE_SPLIT = {
        "accommodation": 0.38,
        "food": 0.27,
        "activities": 0.23,
        "transport": 0.12,
    }

    PREMIUM_BONUS = {
        "accommodation": 0.45,
        "food": 0.25,
        "activities": 0.20,
        "transport": 0.10,
    }

    BUDGET_BONUS = {
        "accommodation": 0.30,
        "food": 0.30,
        "activities": 0.22,
        "transport": 0.18,
    }

    def allocate(
        self,
        total_budget: int,
        total_days: int,
        preferences: AnalyzedPreferences,
    ) -> BudgetAllocationResult:
        split = self.BASE_SPLIT.copy()

        if preferences.focus_budget == "premium":
            split = self.PREMIUM_BONUS
        elif preferences.focus_budget == "budget":
            split = self.BUDGET_BONUS
        elif "food" in preferences.interests:
            split["food"] += 0.05
            split["transport"] -= 0.02
            split["activities"] -= 0.03

        def clamp(value: float) -> int:
            return int(round(max(value, 0) * total_budget))

        breakdown = BudgetBreakdown(
            accommodation=clamp(split["accommodation"]),
            food=clamp(split["food"]),
            activities=clamp(split["activities"]),
            transport=clamp(split["transport"]),
        )

        # Adjust rounding differences
        remainder = total_budget - breakdown.total
        if remainder > 0:
            breakdown.activities += remainder

        per_day = int(total_budget / max(total_days, 1))
        warnings: list[str] = []

        MIN_DAILY_BUDGET = 120_000  # heuristic baseline
        if per_day < MIN_DAILY_BUDGET:
            warnings.append(
                f"예산이 다소 부족합니다. 하루 최소 권장 예산은 {MIN_DAILY_BUDGET:,}원입니다."
            )

        if breakdown.accommodation < total_days * 70_000:
            warnings.append("숙박 예산이 낮습니다. 중급 숙소 기준 밤당 약 70,000원 이상을 권장합니다.")

        return BudgetAllocationResult(breakdown=breakdown, per_day=per_day, warnings=warnings)
