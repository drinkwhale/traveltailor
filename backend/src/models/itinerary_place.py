"""
ItineraryPlace model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    CheckConstraint,
    Index,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class ItineraryPlace(Base):
    """Association between a daily itinerary and a place"""

    __tablename__ = "itinerary_places"
    __table_args__ = (
        CheckConstraint("visit_order >= 1", name="ck_itinerary_place_visit_order"),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0",
            name="ck_itinerary_place_duration",
        ),
        Index("ix_itinerary_places_daily_itinerary_id", "daily_itinerary_id"),
        Index("ix_itinerary_places_place_id", "place_id"),
        Index(
            "ux_itinerary_places_plan_order",
            "daily_itinerary_id",
            "visit_order",
            unique=True,
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daily_itinerary_id = Column(
        UUID(as_uuid=True), ForeignKey("daily_itineraries.id", ondelete="CASCADE"), nullable=False
    )
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    visit_order = Column(Integer, nullable=False)
    visit_time = Column(Time, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    visit_type = Column(String(50), nullable=False)
    estimated_cost = Column(Integer, nullable=True)
    ai_recommendation_reason = Column(Text, nullable=True)
    user_notes = Column(Text, nullable=True)
    is_confirmed = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    daily_itinerary = relationship("DailyItinerary", back_populates="itinerary_places")
    place = relationship("Place", lazy="joined")

    def __repr__(self) -> str:
        return f"<ItineraryPlace itinerary={self.daily_itinerary_id} order={self.visit_order}>"
