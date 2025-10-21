"""Redis-backed cache for AI responses"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Any

try:
    from redis.asyncio import Redis  # type: ignore
except Exception:  # pragma: no cover - redis optional for tests
    Redis = None  # type: ignore

from ...config.settings import settings

logger = logging.getLogger(__name__)


class AIResponseCache:
    """Helper for caching expensive AI outputs"""

    TTL_SECONDS = 60 * 60 * 24 * 7

    def __init__(self) -> None:
        self._redis: Redis | None = None
        self._fallback: dict[str, tuple[dict[str, Any], float]] = {}
        if Redis is not None:
            try:
                self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as exc:  # pragma: no cover - connection issues
                logger.warning("Redis unavailable for AI cache: %s", exc)
                self._redis = None

    @staticmethod
    def build_key(payload: dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"ai-plan:{digest}"

    async def get(self, key: str) -> dict[str, Any] | None:
        if self._redis is not None:
            try:
                value = await self._redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as exc:  # pragma: no cover - network failures
                logger.debug("Redis get failed, falling back to memory cache: %s", exc)

        record = self._fallback.get(key)
        if record:
            return record[0]
        return None

    async def set(self, key: str, value: dict[str, Any]) -> None:
        if self._redis is not None:
            try:
                await self._redis.set(key, json.dumps(value), ex=self.TTL_SECONDS)
                return
            except Exception as exc:  # pragma: no cover
                logger.debug("Redis set failed, using in-memory fallback: %s", exc)

        self._fallback[key] = (value, asyncio.get_event_loop().time() + self.TTL_SECONDS)

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()


cache = AIResponseCache()

