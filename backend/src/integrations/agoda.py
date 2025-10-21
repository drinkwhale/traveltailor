"""
Agoda API client
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, List
from urllib.parse import urlencode

import httpx

from ..config.settings import settings
from ..core.affiliate_tracker import affiliate_tracker

logger = logging.getLogger(__name__)


class AgodaClient:
    """Simplified Agoda API client with graceful fallback"""

    def __init__(self, api_key: str | None = None, *, timeout: float = 20.0) -> None:
        self.api_key = api_key or settings.AGODA_API_KEY
        self.timeout = timeout
        self.base_url = "https://affiliateapi.agoda.com/v2/hotels/search"

    async def search_hotels(
        self,
        *,
        destination: str,
        country: str | None,
        check_in: date,
        nights: int,
        adults: int = 2,
        rooms: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Search accommodation options. Returns mock data when API key is absent or upstream call fails.
        """
        if not destination:
            return []

        if not self.api_key:
            logger.info("Agoda API key missing, returning mock accommodation data")
            return self._build_mock_results(destination, country, check_in, nights, adults)

        params = {
            "city": destination,
            "checkin": check_in.isoformat(),
            "checkout": (check_in + timedelta(days=nights)).isoformat(),
            "adults": adults,
            "rooms": rooms,
            "currency": "KRW",
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Agoda API request failed (%s), using mock data", exc)
            return self._build_mock_results(destination, country, check_in, nights, adults)

        try:
            data = response.json()
            return self._parse_response(data)
        except Exception as exc:
            logger.warning("Agoda response parsing error (%s), using mock data", exc)
            return self._build_mock_results(destination, country, check_in, nights, adults)

    def _parse_response(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize Agoda response"""
        hotels: list[dict[str, Any]] = []
        for item in payload.get("data", []):
            hotels.append(
                {
                    "provider": "Agoda",
                    "name": item.get("name", "Hotel"),
                    "address": item.get("address"),
                    "city": item.get("city"),
                    "country": item.get("country"),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                    "rating": item.get("rating"),
                    "review_count": item.get("reviewCount"),
                    "price_currency": item.get("currency", "KRW"),
                    "price_per_night": int(item.get("pricePerNight", 0)),
                    "total_price": int(item.get("priceTotal", 0)),
                    "booking_url": affiliate_tracker.build_link(item.get("bookingUrl", "")),
                    "image_url": item.get("imageUrl"),
                    "amenities": item.get("amenities", []),
                }
            )
        return hotels

    def _build_mock_results(
        self,
        destination: str,
        country: str | None,
        check_in: date,
        nights: int,
        adults: int,
    ) -> list[dict[str, Any]]:
        """Generate deterministic mock accommodation options"""
        base_price = 110_000
        options: list[dict[str, Any]] = []
        hotels = [
            ("Skyline Residence", 4.5, 1280),
            ("Central Comfort Hotel", 4.2, 980),
            ("Riverfront Boutique Stay", 4.8, 540),
        ]

        checkout = check_in + timedelta(days=nights)

        for index, (name, rating, reviews) in enumerate(hotels):
            price_per_night = base_price + index * 35_000
            total_price = price_per_night * nights
            query = urlencode(
                {
                    "city": destination,
                    "checkin": check_in.isoformat(),
                    "checkout": checkout.isoformat(),
                    "adults": adults,
                    "rooms": 1,
                }
            )
            raw_url = f"https://www.agoda.com/search?{query}"
            options.append(
                {
                    "provider": "Agoda",
                    "name": name,
                    "address": f"{destination} 중심부",
                    "city": destination,
                    "country": country,
                    "latitude": None,
                    "longitude": None,
                    "rating": rating,
                    "review_count": reviews,
                    "price_currency": "KRW",
                    "price_per_night": price_per_night,
                    "total_price": total_price,
                    "booking_url": affiliate_tracker.build_link(raw_url),
                    "image_url": None,
                    "amenities": ["무료 Wi-Fi", "조식 포함", "24시간 프런트"],
                }
            )

        return options


_agoda_client: AgodaClient | None = None


def get_agoda_client() -> AgodaClient:
    """Provide singleton Agoda client"""
    global _agoda_client
    if _agoda_client is None:
        _agoda_client = AgodaClient()
    return _agoda_client
