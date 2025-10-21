"""
Recommendation response schemas
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field


class FlightOptionSchema(BaseModel):
    """Flight option detail"""

    id: UUID
    provider: str
    carrier: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    stops: int
    seat_class: str | None = None
    baggage_info: dict[str, Any] | None = None
    price_currency: str
    price_amount: int
    booking_url: AnyUrl
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlightRecommendationsResponse(BaseModel):
    """Flight recommendation payload"""

    plan_id: UUID
    origin_airport: str
    destination_airport: str
    options: list[FlightOptionSchema] = Field(default_factory=list)


class AccommodationOptionSchema(BaseModel):
    """Accommodation option detail"""

    id: UUID
    provider: str
    name: str
    description: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    rating: float | None = None
    review_count: int | None = None
    star_rating: float | None = None
    price_currency: str
    price_per_night: int | None = None
    total_price: int
    check_in_date: date | None = None
    check_out_date: date | None = None
    nights: int | None = None
    room_type: str | None = None
    booking_url: AnyUrl
    image_url: AnyUrl | None = None
    amenities: list[str] | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccommodationRecommendationsResponse(BaseModel):
    """Accommodation recommendation payload"""

    plan_id: UUID
    check_in: date | None = None
    check_out: date | None = None
    options: list[AccommodationOptionSchema] = Field(default_factory=list)
