"""Schemas for user preference management"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserPreferenceBase(BaseModel):
    """Shared preference attributes"""

    default_budget_min: int | None = None
    default_budget_max: int | None = None
    preferred_traveler_types: list[str] = Field(default_factory=list)
    preferred_interests: list[str] = Field(default_factory=list)
    avoided_activities: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    preferred_accommodation_type: list[str] = Field(default_factory=list)
    mobility_considerations: str | None = None


class UserPreferenceResponse(UserPreferenceBase):
    """API response payload"""

    preferred_pace: str | None = None
    recent_notes: str | None = None
    last_budget_total: int | None = None
    updated_at: str | None = None


class UserPreferenceUpdate(UserPreferenceBase):
    """Update payload for user preferences"""

    pass
