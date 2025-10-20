"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr


class UserSignup(BaseModel):
    """User signup request"""

    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response"""

    id: str
    email: str
    full_name: str | None
    is_active: bool
    subscription_tier: str
    created_at: str

    class Config:
        from_attributes = True
