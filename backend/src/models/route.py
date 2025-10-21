"""
Route model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class Route(Base):
    """Transport leg between two itinerary places"""

    __tablename__ = "routes"
    __table_args__ = (
        CheckConstraint("from_place_id <> to_place_id", name="ck_route_distinct_places"),
        CheckConstraint("from_order < to_order", name="ck_route_order_sequence"),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0", name="ck_route_duration_positive"
        ),
        Index("ix_routes_daily_itinerary_id", "daily_itinerary_id"),
        Index("ix_routes_from_place_id", "from_place_id"),
        Index("ix_routes_to_place_id", "to_place_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daily_itinerary_id = Column(
        UUID(as_uuid=True), ForeignKey("daily_itineraries.id", ondelete="CASCADE"), nullable=False
    )
    from_place_id = Column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    to_place_id = Column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    from_order = Column(Integer, nullable=False)
    to_order = Column(Integer, nullable=False)
    transport_mode = Column(String(50), nullable=False)
    distance_meters = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    estimated_cost = Column(Integer, nullable=True)
    route_polyline = Column(Text, nullable=True)
    instructions = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    daily_itinerary = relationship("DailyItinerary", back_populates="routes")
    from_place = relationship("Place", foreign_keys=[from_place_id], lazy="joined")
    to_place = relationship("Place", foreign_keys=[to_place_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<Route {self.from_place_id}->{self.to_place_id} mode={self.transport_mode}>"
