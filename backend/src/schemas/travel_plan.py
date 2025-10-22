"""
Travel plan schemas
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID
from typing import Any, Literal

from pydantic import Field, field_serializer, field_validator, model_validator

from .itinerary import DailyItineraryResponse
from .base import SanitizedModel


TravelerType = Literal["couple", "family", "solo", "friends"]
PlanStatus = Literal["draft", "in_progress", "completed", "failed", "archived"]


class TravelPreferences(SanitizedModel):
    """Preferences supplied when generating a travel plan"""

    interests: list[str] = Field(default_factory=list)
    must_have: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    pace: Literal["slow", "normal", "fast"] = "normal"
    notes: str | None = None


class TravelPlanCreate(SanitizedModel):
    """Request payload for creating a travel plan"""

    title: str | None = None
    destination: str
    country: str
    start_date: date
    end_date: date
    budget_total: int = Field(..., gt=0)
    traveler_type: TravelerType
    traveler_count: int = Field(default=1, ge=1)
    preferences: TravelPreferences = Field(default_factory=TravelPreferences)

    @model_validator(mode="after")
    def validate_dates(self) -> "TravelPlanCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if len(value) > 140:
            raise ValueError("title must be 140 characters or fewer")
        return value


class BudgetBreakdown(SanitizedModel):
    """Detailed budget allocation"""

    accommodation: int = 0
    food: int = 0
    activities: int = 0
    transport: int = 0

    @property
    def total(self) -> int:
        return self.accommodation + self.food + self.activities + self.transport


class TravelPlanSummary(SanitizedModel):
    """List item summary"""

    id: UUID
    title: str
    destination: str
    start_date: date
    end_date: date
    total_days: int
    total_nights: int
    status: PlanStatus
    budget_total: int
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO 8601 format (RFC-3339 compliant)"""
        return dt.isoformat()

    class Config:
        from_attributes = True


class TravelPlanStatusResponse(SanitizedModel):
    """Status payload for async creation"""

    id: UUID
    status: PlanStatus
    progress: float = Field(default=0, ge=0, le=1)
    message: str | None = None


class TravelPlanUpdate(SanitizedModel):
    """Permitted fields for travel plan patch"""

    title: str | None = None
    status: PlanStatus | None = None
    preferences: dict[str, Any] | None = None


class TravelPlanResponse(SanitizedModel):
    """Detailed travel plan with itineraries"""

    id: UUID
    user_id: UUID
    title: str
    destination: str
    country: str
    start_date: date
    end_date: date
    total_days: int
    total_nights: int
    budget_total: int
    budget_allocated: int | None = None
    budget_breakdown: BudgetBreakdown | None = None
    traveler_type: TravelerType
    traveler_count: int
    preferences: dict[str, Any]
    status: PlanStatus
    ai_model_version: str | None = None
    generation_time_seconds: float | None = None
    created_at: datetime
    updated_at: datetime
    daily_itineraries: list[DailyItineraryResponse] = Field(default_factory=list)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO 8601 format (RFC-3339 compliant)"""
        return dt.isoformat()

    class Config:
        from_attributes = True
