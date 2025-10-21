"""
Place model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Numeric,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func

from ..config.database import Base


class Place(Base):
    """Represents a point of interest or accommodation"""

    __tablename__ = "places"
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_place_latitude"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_place_longitude"),
        CheckConstraint("rating IS NULL OR (rating >= 0 AND rating <= 5)", name="ck_place_rating"),
        CheckConstraint(
            "price_level IS NULL OR (price_level >= 1 AND price_level <= 4)",
            name="ck_place_price_level",
        ),
        Index("ix_places_external_id", "external_id"),
        Index("ix_places_city", "city"),
        Index("ix_places_category", "category"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), nullable=True)
    external_source = Column(String(50), nullable=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    rating = Column(Numeric(2, 1), nullable=True)
    price_level = Column(Integer, nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(Text, nullable=True)
    opening_hours = Column(JSONB, nullable=True)
    photos = Column(ARRAY(Text), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Place {self.name} ({self.category})>"
