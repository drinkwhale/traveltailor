"""
Base schemas for API responses
"""

from typing import Generic, Optional, TypeVar, Any

from pydantic import BaseModel, model_validator

from ..utils.sanitizer import sanitize_payload

T = TypeVar("T")


class SanitizedModel(BaseModel):
    """Mixin that sanitises incoming payloads to mitigate injection/XSS."""

    @model_validator(mode="before")
    @classmethod
    def _sanitize(cls, values: Any) -> Any:
        return sanitize_payload(values)


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response format"""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @staticmethod
    def create(items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        """Create paginated response"""
        total_pages = (total + page_size - 1) // page_size
        return PaginatedResponse(
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )
