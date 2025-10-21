"""
Skyscanner API client
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, List

import httpx

from ..config.settings import settings

logger = logging.getLogger(__name__)


class SkyscannerClient:
    """Lightweight client for retrieving flight recommendations from Skyscanner"""

    def __init__(self, api_key: str | None = None, *, timeout: float = 20.0) -> None:
        self.api_key = api_key or settings.SKYSCANNER_API_KEY
        self.timeout = timeout
        self.base_url = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create"

    async def search_round_trip(
        self,
        *,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        adults: int = 1,
        cabin_class: str = "economy",
    ) -> list[dict[str, Any]]:
        """
        Search for round trip flights

        Returns:
            List of normalized flight itineraries. Fallback mock data is used when the API key is missing
            or the upstream service fails.
        """
        if not origin or not destination:
            return []

        if not self.api_key:
            logger.info("Skyscanner API key missing, returning mock data")
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

        payload = {
            "query": {
                "market": "KR",
                "locale": "ko-KR",
                "currency": "KRW",
                "cabinClass": cabin_class,
                "adults": adults,
                "originPlaceId": {"iata": origin},
                "destinationPlaceId": {"iata": destination},
                "dateInterval": {
                    "startDate": departure_date.isoformat(),
                    "endDate": return_date.isoformat(),
                },
            }
        }

        headers = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Skyscanner API request failed (%s), using mock data", exc)
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

        try:
            data = response.json()
            return self._parse_response(data)
        except Exception as exc:
            logger.warning("Skyscanner response parsing error (%s), using mock data", exc)
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

    def _parse_response(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize Skyscanner response into internal representation"""
        itineraries = payload.get("content", {}).get("results", {}).get("itineraries", {})
        legs = payload.get("content", {}).get("results", {}).get("segments", {})

        normalized: list[dict[str, Any]] = []
        for itinerary_id, itinerary in itineraries.items():
            pricing_options = itinerary.get("pricingOptions", [])
            if not pricing_options:
                continue

            leg_ids: Iterable[str] = itinerary.get("legIds", [])
            segments: list[dict[str, Any]] = []
            for leg_id in leg_ids:
                leg = legs.get(leg_id)
                if not leg:
                    continue
                segments.append(self._normalize_segment(leg))

            if not segments:
                continue

            price = pricing_options[0].get("price", {})
            normalized.append(
                {
                    "provider": "Skyscanner",
                    "carrier": segments[0]["carrier"],
                    "flight_number": segments[0]["flight_number"],
                    "departure_airport": segments[0]["departure_airport"],
                    "arrival_airport": segments[-1]["arrival_airport"],
                    "departure_time": segments[0]["departure_time"],
                    "arrival_time": segments[-1]["arrival_time"],
                    "duration_minutes": sum(seg["duration_minutes"] for seg in segments),
                    "stops": max(len(segments) - 1, 0),
                    "seat_class": itinerary.get("cabinClass", "economy"),
                    "price_currency": price.get("currency", "KRW"),
                    "price_amount": int(price.get("amount", 0)),
                    "booking_url": pricing_options[0].get("deeplinkUrl", ""),
                    "baggage_info": pricing_options[0].get("items", [{}])[0].get("baggage", {}),
                }
            )

        return normalized

    @staticmethod
    def _normalize_segment(segment: dict[str, Any]) -> dict[str, Any]:
        """Extract minimal segment information from API segment payload"""
        departure = segment.get("departureDateTime")
        arrival = segment.get("arrivalDateTime")

        def _to_datetime(value: str | None) -> datetime:
            if not value:
                return datetime.now(timezone.utc)
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return {
            "carrier": segment.get("marketingCarrier", {}).get("name", "Unknown Carrier"),
            "flight_number": segment.get("flightNumber", "XX000"),
            "departure_airport": segment.get("origin", {}).get("airport", {}).get("iata", "UNK"),
            "arrival_airport": segment.get("destination", {}).get("airport", {}).get("iata", "UNK"),
            "departure_time": _to_datetime(departure),
            "arrival_time": _to_datetime(arrival),
            "duration_minutes": int(segment.get("durationInMinutes") or 0),
        }

    def _build_mock_results(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        *,
        adults: int,
        cabin_class: str,
    ) -> list[dict[str, Any]]:
        """Generate deterministic mock flight options"""
        base_departure = datetime.combine(departure_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        base_return = datetime.combine(return_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )

        options: list[dict[str, Any]] = []
        base_price = 320_000
        carriers = [
            ("Korean Air", "KE703"),
            ("Asiana Airlines", "OZ1085"),
            ("ANA", "NH862"),
        ]

        for index, (carrier, flight_number) in enumerate(carriers):
            departure_time = base_departure + timedelta(hours=9 + index * 2)
            arrival_time = departure_time + timedelta(hours=2 + index)
            price_amount = base_price + index * 45_000
            options.append(
                {
                    "provider": "Skyscanner",
                    "carrier": carrier,
                    "flight_number": flight_number,
                    "departure_airport": origin,
                    "arrival_airport": destination,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration_minutes": int((arrival_time - departure_time).total_seconds() // 60),
                    "stops": 0 if index == 0 else 1,
                    "seat_class": cabin_class,
                    "price_currency": "KRW",
                    "price_amount": price_amount * adults,
                    "booking_url": (
                        f"https://www.skyscanner.net/transport/flights/{origin}/{destination}/"
                        f"{departure_date.strftime('%y%m%d')}/{return_date.strftime('%y%m%d')}/"
                        f"?adults={adults}&cabin={cabin_class}"
                    ),
                    "baggage_info": {"carry_on": "7kg", "checked": "23kg"},
                }
            )

        return options


# Singleton helper
_skyscanner_client: SkyscannerClient | None = None


def get_skyscanner_client() -> SkyscannerClient:
    """Provide a singleton Skyscanner client"""
    global _skyscanner_client
    if _skyscanner_client is None:
        _skyscanner_client = SkyscannerClient()
    return _skyscanner_client
