"""
DailyItinerary model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    String,
    Date,
    Integer,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class DailyItinerary(Base):
    """Represents a daily plan within a travel plan"""

    __tablename__ = "daily_itineraries"
    __table_args__ = (
        CheckConstraint("day_number >= 1", name="ck_daily_itinerary_day_number"),
        Index("ix_daily_itineraries_travel_plan_id", "travel_plan_id"),
        Index("ux_daily_itineraries_plan_day", "travel_plan_id", "day_number", unique=True),
        Index("ux_daily_itineraries_plan_date", "travel_plan_id", "date", unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    travel_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("travel_plans.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    day_number = Column(Integer, nullable=False)
    theme = Column(String(100), nullable=True)
    notes = Column(String, nullable=True)
    weather_forecast = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    travel_plan = relationship("TravelPlan", back_populates="daily_itineraries")
    itinerary_places = relationship(
        "ItineraryPlace",
        back_populates="daily_itinerary",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    routes = relationship(
        "Route",
        back_populates="daily_itinerary",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DailyItinerary plan={self.travel_plan_id} day={self.day_number}>"
