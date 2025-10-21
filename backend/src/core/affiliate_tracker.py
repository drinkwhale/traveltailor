"""
Affiliate tracking utilities
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def _clean_params(params: Mapping[str, str | None]) -> dict[str, str]:
    """Remove empty parameters"""
    return {key: value for key, value in params.items() if value}


@dataclass(slots=True)
class AffiliateTracker:
    """Append UTM and affiliate parameters to outbound links"""

    defaults: dict[str, str] = field(
        default_factory=lambda: {
            "utm_source": "traveltailor",
            "utm_medium": "affiliate",
            "utm_campaign": "itinerary_recommendations",
        }
    )

    def build_link(self, url: str, *, extra: Mapping[str, str] | None = None) -> str:
        """Return URL with tracking parameters appended"""
        if not url:
            raise ValueError("url is required for affiliate tracking")

        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query.update(self.defaults)
        if extra:
            query.update(_clean_params(extra))

        new_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=new_query))


# Shared tracker instance
affiliate_tracker = AffiliateTracker()
