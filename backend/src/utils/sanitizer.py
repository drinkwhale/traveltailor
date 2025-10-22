"""
Utility helpers for sanitising user supplied payloads on the backend.

The goal is to keep the backend defensive even though the frontend already
applies DOMPurify.  Sanitisation here focuses on stripping script/style tags,
event handler attributes and javascript: URLs that could leak into templates or
logs.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


SCRIPT_TAG_RE = re.compile(r"<\s*(script|style)[^>]*>.*?<\s*/\s*\1\s*>", re.IGNORECASE | re.DOTALL)
EVENT_HANDLER_RE = re.compile(r"on[a-z]+\s*=", re.IGNORECASE)
JS_PROTOCOL_RE = re.compile(r"javascript\s*:", re.IGNORECASE)
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


def sanitize_string(value: str) -> str:
    """Return a defensively sanitised string."""
    normalised = unicodedata.normalize("NFKC", value)
    stripped = SCRIPT_TAG_RE.sub("", normalised)
    stripped = EVENT_HANDLER_RE.sub("", stripped)
    stripped = JS_PROTOCOL_RE.sub("", stripped)
    stripped = CONTROL_CHAR_RE.sub("", stripped)
    return stripped.strip()


def sanitize_payload(payload: Any) -> Any:
    """
    Recursively sanitise strings inside nested payloads.

    Works for lists, tuples and dicts.  Non-string primitives are returned
    unchanged.
    """
    if isinstance(payload, str):
        return sanitize_string(payload)
    if isinstance(payload, dict):
        return {key: sanitize_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(sanitize_payload(item) for item in payload)
    return payload
