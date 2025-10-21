"""Timeline generation helpers"""

from __future__ import annotations

from datetime import timedelta, time
from itertools import cycle, islice
from typing import Iterable

from ...schemas.travel_plan import TravelPlanCreate
from .budget_allocator import BudgetAllocationResult
from .preference_analyzer import AnalyzedPreferences
from .types import DailyItineraryDraft, ItineraryPlaceDraft, TravelPlanDraft
from ..places.recommender import RecommendationBundle
from ..routes.optimizer import RoutesOptimizer


class TimelineGenerator:
    """Generate per-day itineraries from recommended places"""

    def __init__(self) -> None:
        self.routes_optimizer = RoutesOptimizer()

    def _cycle(self, items: Iterable) -> Iterable:
        return cycle(items) if items else cycle([None])

    def build_daily_itineraries(
        self,
        plan_request: TravelPlanCreate,
        draft: TravelPlanDraft,
        bundle: RecommendationBundle,
        preferences: AnalyzedPreferences,
        budget: BudgetAllocationResult,
    ) -> list[DailyItineraryDraft]:
        total_days = draft.total_days
        start_date = draft.start_date

        accommodation_iter = self._cycle(bundle.accommodations)
        activity_iter = self._cycle(bundle.activities)
        restaurant_iter = self._cycle(bundle.restaurants)
        cafe_iter = self._cycle(bundle.cafes)

        themes = preferences.interests or ["local highlights"]

        itineraries: list[DailyItineraryDraft] = []

        for day in range(total_days):
            date_value = start_date + timedelta(days=day)
            theme = themes[day % len(themes)]

            places: list[ItineraryPlaceDraft] = []
            order = 1

            accommodation = next(accommodation_iter)
            if accommodation:
                places.append(
                    ItineraryPlaceDraft(
                        place=accommodation,
                        visit_order=order,
                        visit_type="overnight",
                        visit_time=time(8, 0),
                        duration_minutes=120,
                        estimated_cost=int(budget.breakdown.accommodation / total_days),
                        ai_recommendation_reason="Convenient base for the day",
                    )
                )
                order += 1

            morning_activity = next(activity_iter)
            if morning_activity:
                places.append(
                    ItineraryPlaceDraft(
                        place=morning_activity,
                        visit_order=order,
                        visit_type="activity",
                        visit_time=time(10, 0),
                        duration_minutes=150,
                        estimated_cost=int(budget.breakdown.activities / (total_days * 2)),
                        ai_recommendation_reason="Signature experience aligned with interests",
                    )
                )
                order += 1

            lunch_spot = next(restaurant_iter)
            if lunch_spot:
                places.append(
                    ItineraryPlaceDraft(
                        place=lunch_spot,
                        visit_order=order,
                        visit_type="meal",
                        visit_time=time(13, 0),
                        duration_minutes=90,
                        estimated_cost=int(budget.breakdown.food / (total_days * 2)),
                        ai_recommendation_reason="Popular dining spot featuring local flavours",
                    )
                )
                order += 1

            afternoon_activity = next(activity_iter)
            if afternoon_activity:
                places.append(
                    ItineraryPlaceDraft(
                        place=afternoon_activity,
                        visit_order=order,
                        visit_type="activity",
                        visit_time=time(15, 30),
                        duration_minutes=120,
                        estimated_cost=int(budget.breakdown.activities / (total_days * 2)),
                        ai_recommendation_reason="Complementary experience for the day",
                    )
                )
                order += 1

            cafe_break = next(cafe_iter)
            if cafe_break:
                places.append(
                    ItineraryPlaceDraft(
                        place=cafe_break,
                        visit_order=order,
                        visit_type="meal",
                        visit_time=time(17, 0),
                        duration_minutes=60,
                        estimated_cost=int(budget.breakdown.food / (total_days * 4)),
                        ai_recommendation_reason="Relaxing cafe stop before evening",
                    )
                )
                order += 1

            dinner_spot = next(restaurant_iter)
            if dinner_spot:
                places.append(
                    ItineraryPlaceDraft(
                        place=dinner_spot,
                        visit_order=order,
                        visit_type="meal",
                        visit_time=time(19, 30),
                        duration_minutes=90,
                        estimated_cost=int(budget.breakdown.food / (total_days * 2)),
                        ai_recommendation_reason="Chef-recommended dinner",
                    )
                )
                order += 1

            itinerary = DailyItineraryDraft(
                date=date_value,
                day_number=day + 1,
                theme=f"{theme.title()} Day",
                notes="Balanced schedule generated via TravelTailor heuristics",
                places=places,
            )

            itinerary.routes = self.routes_optimizer.build_routes(itinerary)
            itineraries.append(itinerary)

        draft.daily_itineraries = itineraries
        return itineraries

