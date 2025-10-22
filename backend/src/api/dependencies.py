"""
Shared FastAPI dependencies and utilities.

This module hosts the SlowAPI limiter instance so the configuration is centralised.
Routers can import `limiter` directly and decorate handlers with `@limiter.limit`.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

from fastapi import Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config.database import get_db
from ..config.settings import settings

TFunc = TypeVar("TFunc", bound=Callable[..., Awaitable[Any]])

# Initialise SlowAPI limiter.  The same instance is reused by `main.py`.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    headers_enabled=True,
)


def rate_limit(limit: str) -> Callable[[TFunc], TFunc]:
    """
    Curried decorator wrapper that applies SlowAPI limits while keeping typing intact.

    Example:
        @router.post("/login")
        @rate_limit(settings.RATE_LIMIT_AUTH)
        async def login(...):
            ...
    """

    def decorator(func: TFunc) -> TFunc:
        return limiter.limit(limit)(func)  # type: ignore[return-value]

    return decorator


def user_rate_limit(limit: str) -> Callable[[TFunc], TFunc]:
    """
    Rate limit requests using authenticated user ID instead of IP address.

    The wrapped endpoint **must** receive a `Request` object and an authenticated
    `user_id` (string) parameter.  This allows high-volume clients behind NAT to
    have independent quotas after login.
    """

    def _key_func(request: Request) -> str:
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        if user_id:
            return f"user:{user_id}"
        return get_remote_address(request)

    scoped_limiter = Limiter(key_func=_key_func, headers_enabled=True)

    def decorator(func: TFunc) -> TFunc:
        return scoped_limiter.limit(limit)(func)  # type: ignore[return-value]

    return decorator


# Re-export get_db for convenience so routers can import from a single module.
DatabaseDependency = Depends(get_db)

__all__ = ["limiter", "rate_limit", "user_rate_limit", "DatabaseDependency"]
