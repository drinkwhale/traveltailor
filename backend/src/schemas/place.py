"""
Place schemas
"""

from __future__ import annotations

from datetime import time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


PlaceCategory = Literal[
    "accommodation",
    "restaurant",
    "cafe",
    "attraction",
    "shopping",
    "transport",
]


class PlaceBase(BaseModel):
    """Common fields for place objects"""

    name: str
    category: PlaceCategory
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str | None = None
    city: str | None = None
    country: str | None = None
    subcategory: str | None = None
    description: str | None = None
    phone: str | None = None
    website: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    price_level: int | None = Field(default=None, ge=1, le=4)
    opening_hours: dict | None = None
    photos: list[str] | None = None
    tags: list[str] | None = None


class PlaceCreate(PlaceBase):
    """Payload to create a place"""

    external_id: str | None = None
    external_source: str | None = None


class PlaceResponse(PlaceBase):
    """Place representation returned from API"""

    id: UUID
    external_id: str | None = None
    external_source: str | None = None

    class Config:
        from_attributes = True


class ItineraryPlaceSummary(BaseModel):
    """Lightweight place representation within an itinerary"""

    id: UUID
    place_id: UUID
    name: str
    category: PlaceCategory
    latitude: float
    longitude: float
    visit_order: int
    visit_type: Literal["overnight", "meal", "activity", "transit"]
    visit_time: time | None = None
    duration_minutes: int | None = None
    estimated_cost: int | None = None
    ai_recommendation_reason: str | None = None
    user_notes: str | None = None
    is_confirmed: bool = True

    class Config:
        from_attributes = True
