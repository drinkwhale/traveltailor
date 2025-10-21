"""
Itinerary schemas
"""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .place import ItineraryPlaceSummary


TransportMode = Literal["walking", "driving", "public_transit", "taxi", "bicycle"]


class RouteResponse(BaseModel):
    """Route segment between itinerary places"""

    id: UUID
    daily_itinerary_id: UUID
    from_place_id: UUID
    to_place_id: UUID
    from_order: int
    to_order: int
    transport_mode: TransportMode
    distance_meters: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=0)
    estimated_cost: int | None = Field(default=None, ge=0)
    route_polyline: str | None = None
    instructions: dict | None = None

    class Config:
        from_attributes = True


class DailyItineraryResponse(BaseModel):
    """Daily itinerary with places and routes"""

    id: UUID
    travel_plan_id: UUID
    date: date
    day_number: int = Field(..., ge=1)
    theme: str | None = None
    notes: str | None = None
    weather_forecast: dict | None = None
    places: list[ItineraryPlaceSummary]
    routes: list[RouteResponse]

    class Config:
        from_attributes = True

