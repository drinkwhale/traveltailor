"""
Dataclasses used within AI planning pipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any

from ...schemas.place import PlaceCreate
from ...schemas.travel_plan import BudgetBreakdown, TravelPreferences


@dataclass
class ItineraryPlaceDraft:
    """Draft of a place visit before persistence"""

    place: PlaceCreate
    visit_order: int
    visit_type: str
    visit_time: time | None = None
    duration_minutes: int | None = None
    estimated_cost: int | None = None
    ai_recommendation_reason: str | None = None
    user_notes: str | None = None


@dataclass
class RouteDraft:
    """Draft route between two itinerary places"""

    from_order: int
    to_order: int
    transport_mode: str
    distance_meters: int | None = None
    duration_minutes: int | None = None
    estimated_cost: int | None = None
    route_polyline: str | None = None
    instructions: dict[str, Any] | None = None


@dataclass
class DailyItineraryDraft:
    """Draft daily itinerary composed of places and routes"""

    date: date
    day_number: int
    theme: str
    notes: str | None = None
    weather_forecast: dict[str, Any] | None = None
    places: list[ItineraryPlaceDraft] = field(default_factory=list)
    routes: list[RouteDraft] = field(default_factory=list)


@dataclass
class TravelPlanDraft:
    """Draft travel plan metadata"""

    title: str
    destination: str
    country: str
    start_date: date
    end_date: date
    total_days: int
    total_nights: int
    budget_total: int
    traveler_type: str
    traveler_count: int
    preferences: TravelPreferences
    budget_breakdown: BudgetBreakdown
    ai_model_version: str | None = None
    generation_time_seconds: float | None = None
    daily_itineraries: list[DailyItineraryDraft] = field(default_factory=list)

