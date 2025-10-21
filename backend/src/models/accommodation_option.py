"""
AccommodationOption model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class AccommodationOption(Base):
    """Persisted accommodation recommendation associated with a travel plan"""

    __tablename__ = "accommodation_options"
    __table_args__ = (
        CheckConstraint(
            "price_per_night IS NULL OR price_per_night >= 0",
            name="ck_accommodation_option_price_per_night",
        ),
        CheckConstraint("total_price >= 0", name="ck_accommodation_option_total_price"),
        CheckConstraint(
            "rating IS NULL OR (rating >= 0 AND rating <= 5)",
            name="ck_accommodation_option_rating",
        ),
        CheckConstraint(
            "review_count IS NULL OR review_count >= 0",
            name="ck_accommodation_option_reviews",
        ),
        CheckConstraint(
            "nights IS NULL OR nights >= 1",
            name="ck_accommodation_option_nights",
        ),
        Index("ix_accommodation_options_plan_id", "travel_plan_id"),
        Index("ix_accommodation_options_total_price", "total_price"),
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
        default="Booking.com",
        server_default="Booking.com",
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    rating = Column(Numeric(2, 1), nullable=True)
    review_count = Column(Integer, nullable=True)
    star_rating = Column(Numeric(2, 1), nullable=True)
    price_currency = Column(
        String(3),
        nullable=False,
        default="KRW",
        server_default="KRW",
    )
    price_per_night = Column(Integer, nullable=True)
    total_price = Column(Integer, nullable=False)
    check_in_date = Column(Date, nullable=True)
    check_out_date = Column(Date, nullable=True)
    nights = Column(Integer, nullable=True)
    room_type = Column(String(100), nullable=True)
    booking_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    amenities = Column(ARRAY(Text), nullable=True)
    tags = Column(ARRAY(String(50)), nullable=True)
    policies = Column(JSONB, nullable=True)
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

    travel_plan = relationship("TravelPlan", back_populates="accommodation_options")

    def __repr__(self) -> str:
        return f"<AccommodationOption {self.name} ({self.provider})>"
