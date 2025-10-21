"""
User model
사용자 계정 정보
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..config.database import Base


class User(Base):
    """User 모델"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(String(20), default="free", nullable=False)

    # Relationships
    preference = relationship("UserPreference", back_populates="user", uselist=False)
    travel_plans = relationship("TravelPlan", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
