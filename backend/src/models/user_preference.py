"""
UserPreference model
사용자 여행 선호도 저장
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..config.database import Base


class UserPreference(Base):
    """UserPreference 모델"""

    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Budget preferences
    default_budget_min = Column(Integer, nullable=True)
    default_budget_max = Column(Integer, nullable=True)

    # Travel preferences
    preferred_traveler_types = Column(ARRAY(String), nullable=True)
    preferred_interests = Column(ARRAY(String), nullable=True)
    avoided_activities = Column(ARRAY(String), nullable=True)
    dietary_restrictions = Column(ARRAY(String), nullable=True)
    mobility_considerations = Column(Text, nullable=True)
    preferred_accommodation_type = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="preference")

    def __repr__(self) -> str:
        return f"<UserPreference user_id={self.user_id}>"
