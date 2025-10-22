"""
Authentication schemas
"""

from pydantic import EmailStr, Field, field_validator

from .base import SanitizedModel


class UserSignup(SanitizedModel):
    """User signup request"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value and len(value) > 120:
            raise ValueError("full_name must be 120 characters or fewer")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if " " in value:
            raise ValueError("password must not contain spaces")
        return value


class UserLogin(SanitizedModel):
    """User login request"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class Token(SanitizedModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"


class UserResponse(SanitizedModel):
    """User response"""

    id: str
    email: str
    full_name: str | None
    is_active: bool
    subscription_tier: str
    created_at: str

    class Config:
        from_attributes = True
