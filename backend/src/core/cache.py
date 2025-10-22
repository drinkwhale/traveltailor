"""
Redis-backed caching utilities for high-frequency travel data.

This module centralises Redis connection handling and offers helpers that
specialise in the two hottest paths identified in profiling:

1. Place detail enrichment (Google Places, internal heuristics)
2. Flight price searches (Skyscanner API)

Both payloads are relatively small JSON blobs that benefit from short-lived
TTL based caching.  The helpers below provide a minimal API that hides
connection management, serialisation and cache key conventions from callers.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Literal, TypedDict

from redis.asyncio import Redis

from ..config.settings import settings

logger = logging.getLogger(__name__)

_redis_pool: Redis | None = None
_redis_lock = asyncio.Lock()


def _build_namespaced_key(namespace: str, identifier: str) -> str:
    """Construct a stable cache key with service namespace."""
    return f"traveltailor:{namespace}:{identifier}"


async def get_redis_client() -> Redis:
    """
    Return a singleton Redis client.

    Lazily initialises the connection so unit tests can patch the module easily.
    """
    global _redis_pool

    if _redis_pool is not None:
        return _redis_pool

    async with _redis_lock:
        if _redis_pool is None:
            logger.info("Initialising Redis connection to %s", settings.REDIS_URL)
            _redis_pool = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                health_check_interval=30,
            )
    return _redis_pool


async def close_redis_client() -> None:
    """Gracefully close the Redis connection."""
    global _redis_pool
    if _redis_pool is None:
        return
    try:
        await _redis_pool.close()
        await _redis_pool.wait_closed()
    finally:
        _redis_pool = None


class CachedFlightQuote(TypedDict, total=False):
    """Structured payload stored for flight quote responses."""

    origin: str
    destination: str
    departure_date: str
    return_date: str
    traveler_count: int
    currency: str
    price_amount: int
    provider: str
    raw: dict[str, Any]


@dataclass(slots=True)
class CacheTTL:
    """Simple value object encapsulating TTL defaults."""

    places: int = settings.REDIS_TTL_PLACES
    flights: int = settings.REDIS_TTL_FLIGHTS


ttl_config = CacheTTL()


async def _get_json(namespace: str, identifier: str) -> dict[str, Any] | None:
    client = await get_redis_client()
    raw = await client.get(_build_namespaced_key(namespace, identifier))
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to decode cached payload for %s:%s", namespace, identifier)
        await client.delete(_build_namespaced_key(namespace, identifier))
    return None


async def _set_json(
    namespace: str,
    identifier: str,
    payload: dict[str, Any],
    *,
    ttl: int,
) -> None:
    client = await get_redis_client()
    key = _build_namespaced_key(namespace, identifier)
    await client.set(key, json.dumps(payload), ex=ttl)


async def _invalidate(namespace: str, identifier: str | None = None) -> int:
    client = await get_redis_client()
    if identifier:
        return await client.delete(_build_namespaced_key(namespace, identifier))

    pattern = f"traveltailor:{namespace}:*"
    keys = [key async for key in client.scan_iter(match=pattern)]
    if not keys:
        return 0
    return await client.delete(*keys)


async def get_cached_place(place_id: str) -> dict[str, Any] | None:
    """Return cached place metadata if available."""
    return await _get_json("places", place_id)


async def cache_place(place_id: str, payload: dict[str, Any], *, ttl: int | None = None) -> None:
    """Store place payload in Redis."""
    await _set_json("places", place_id, payload, ttl=ttl or ttl_config.places)


async def invalidate_place_cache(place_id: str | None = None) -> int:
    """Invalidate a single place entry or the entire namespace."""
    return await _invalidate("places", place_id)


async def get_cached_flight_quote(key: str) -> CachedFlightQuote | None:
    """Return cached flight quote, if present."""
    data = await _get_json("flight_quotes", key)
    if data is None:
        return None
    return CachedFlightQuote(**data)


async def cache_flight_quote(
    key: str,
    payload: CachedFlightQuote,
    *,
    ttl: int | None = None,
) -> None:
    """Persist flight quote payload for given key."""
    await _set_json("flight_quotes", key, dict(payload), ttl=ttl or ttl_config.flights)


async def invalidate_flight_cache(identifier: str | None = None) -> int:
    """Invalidate cached flight quotes."""
    return await _invalidate("flight_quotes", identifier)


async def cached_operation(
    namespace: Literal["places", "flight_quotes"],
    identifier: str,
    producer: Callable[[], Any],
    *,
    ttl: int,
) -> Any:
    """
    Generic helper that either returns cached payload or executes producer.

    Intended primarily for async call sites (Google Places enrichment, Skyscanner
    round trips). The helper gracefully handles JSON serialisation errors and
    invalidates corrupted values automatically.
    """
    cached = await _get_json(namespace, identifier)
    if cached is not None:
        return cached

    result = await producer()
    if isinstance(result, dict):
        await _set_json(namespace, identifier, result, ttl=ttl)
    else:
        logger.debug(
            "Skip caching for %s:%s because payload is not serialisable dict (%s)",
            namespace,
            identifier,
            type(result),
        )
    return result
