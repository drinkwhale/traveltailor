"""
Booking.com affiliate utilities
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping
from urllib.parse import urlencode

from ..config.settings import settings
from ..core.affiliate_tracker import AffiliateTracker, affiliate_tracker

logger = logging.getLogger(__name__)

_slug_pattern = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    """Convert a string into a Booking-compatible slug"""
    value = value.lower()
    value = _slug_pattern.sub("-", value).strip("-")
    return value or "property"


@dataclass
class BookingAffiliateClient:
    """Helper for generating Booking.com deep links with affiliate tracking"""

    tracker: AffiliateTracker = field(default_factory=lambda: affiliate_tracker)
    partner_id: str | None = field(default_factory=lambda: settings.BOOKING_COM_AFFILIATE_ID)

    def build_hotel_link(
        self,
        *,
        hotel_name: str,
        city: str | None,
        currency: str | None,
        check_in: date | None,
        check_out: date | None,
        params: Mapping[str, str] | None = None,
    ) -> str:
        """Return a Booking.com hotel URL with affiliate parameters"""
        slug_city = _slugify(city or "city")
        slug_name = _slugify(hotel_name)
        base_url = f"https://www.booking.com/hotel/{slug_city}/{slug_name}.html"

        query: dict[str, str] = {}
        if check_in:
            query["checkin"] = check_in.isoformat()
        if check_out:
            query["checkout"] = check_out.isoformat()
        if currency:
            query["selected_currency"] = currency.upper()
        if params:
            query.update({key: value for key, value in params.items() if value})

        if self.partner_id:
            query["aid"] = self.partner_id
        else:
            logger.info("Booking.com partner ID not configured; generating non-affiliate link")

        raw_url = f"{base_url}?{urlencode(query)}" if query else base_url
        return self.tracker.build_link(raw_url)


# Shared instance
booking_affiliate = BookingAffiliateClient()
