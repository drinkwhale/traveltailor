"""
FlightOption model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class FlightOption(Base):
    """Persisted flight recommendation associated with a travel plan"""

    __tablename__ = "flight_options"
    __table_args__ = (
        CheckConstraint("price_amount >= 0", name="ck_flight_option_price_non_negative"),
        CheckConstraint("duration_minutes > 0", name="ck_flight_option_duration_positive"),
        CheckConstraint("stops >= 0", name="ck_flight_option_stops_non_negative"),
        Index("ix_flight_options_plan_id", "travel_plan_id"),
        Index("ix_flight_options_price", "price_amount"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    travel_plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("travel_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider = Column(
        String(50),
        nullable=False,
        default="Skyscanner",
        server_default="Skyscanner",
    )
    carrier = Column(String(100), nullable=False)
    flight_number = Column(String(20), nullable=False)
    departure_airport = Column(String(10), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    stops = Column(Integer, nullable=False, default=0, server_default="0")
    seat_class = Column(String(50), nullable=True)
    baggage_info = Column(JSONB, nullable=True)
    price_currency = Column(
        String(3),
        nullable=False,
        default="KRW",
        server_default="KRW",
    )
    price_amount = Column(Integer, nullable=False)
    booking_url = Column(Text, nullable=False)
    affiliate_code = Column(String(50), nullable=True)
    last_synced_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    travel_plan = relationship("TravelPlan", back_populates="flight_options")

    def __repr__(self) -> str:
        return (
            f"<FlightOption {self.flight_number} "
            f"{self.departure_airport}->{self.arrival_airport}>"
        )
