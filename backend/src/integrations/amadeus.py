"""
Amadeus API client for flight search
https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api-reference
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

from ..config.settings import settings

logger = logging.getLogger(__name__)


class AmadeusClient:
    """Lightweight client for retrieving flight recommendations from Amadeus"""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key or settings.AMADEUS_API_KEY
        self.api_secret = api_secret or settings.AMADEUS_API_SECRET
        self.timeout = timeout
        self.base_url = "https://test.api.amadeus.com"  # Test environment
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

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
        Search for round trip flights using Amadeus Flight Offers Search API

        Returns:
            List of normalized flight itineraries. Fallback mock data is used when the API key is missing
            or the upstream service fails.
        """
        if not origin or not destination:
            return []

        if not self.api_key or not self.api_secret:
            logger.info("Amadeus API credentials missing, returning mock data")
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

        # Ensure we have a valid access token
        try:
            await self._ensure_access_token()
        except Exception as exc:
            logger.warning("Amadeus token acquisition failed (%s), using mock data", exc)
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

        # Map cabin class to Amadeus format
        travel_class_map = {
            "economy": "ECONOMY",
            "premium_economy": "PREMIUM_ECONOMY",
            "business": "BUSINESS",
            "first": "FIRST",
        }
        travel_class = travel_class_map.get(cabin_class.lower(), "ECONOMY")

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date.isoformat(),
            "returnDate": return_date.isoformat(),
            "adults": adults,
            "travelClass": travel_class,
            "currencyCode": "KRW",
            "max": 10,  # Maximum number of results
        }

        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v2/shopping/flight-offers",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Amadeus API request failed (%s), using mock data", exc)
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
            logger.warning("Amadeus response parsing error (%s), using mock data", exc)
            return self._build_mock_results(
                origin,
                destination,
                departure_date,
                return_date,
                adults=adults,
                cabin_class=cabin_class,
            )

    async def _ensure_access_token(self) -> None:
        """Ensure we have a valid OAuth access token"""
        now = datetime.now(timezone.utc)

        # Check if we have a valid token
        if self._access_token and self._token_expires_at:
            if now < self._token_expires_at - timedelta(minutes=5):
                return

        # Request a new token
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 1800)  # Default 30 minutes
            self._token_expires_at = now + timedelta(seconds=expires_in)

    def _parse_response(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize Amadeus response into internal representation"""
        offers = payload.get("data", [])
        dictionaries = payload.get("dictionaries", {})

        normalized: list[dict[str, Any]] = []
        for offer in offers:
            try:
                normalized_offer = self._normalize_offer(offer, dictionaries)
                if normalized_offer:
                    normalized.append(normalized_offer)
            except Exception as exc:
                logger.warning("Failed to normalize offer: %s", exc)
                continue

        return normalized

    def _normalize_offer(
        self, offer: dict[str, Any], dictionaries: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Convert a single Amadeus offer to our internal format"""
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            return None

        price = offer.get("price", {})
        price_amount = float(price.get("total", 0))

        # Get outbound itinerary (first one)
        outbound = itineraries[0]
        segments = outbound.get("segments", [])
        if not segments:
            return None

        first_segment = segments[0]
        last_segment = segments[-1]

        # Extract carrier information
        carrier_code = first_segment.get("carrierCode", "XX")
        carriers = dictionaries.get("carriers", {})
        carrier_name = carriers.get(carrier_code, carrier_code)

        # Calculate total duration
        duration_str = outbound.get("duration", "PT0M")
        duration_minutes = self._parse_duration(duration_str)

        # Parse departure and arrival times
        departure_time = self._parse_datetime(first_segment.get("departure", {}).get("at"))
        arrival_time = self._parse_datetime(last_segment.get("arrival", {}).get("at"))

        # Count stops (segments - 1)
        stops = max(len(segments) - 1, 0)

        # Get cabin class
        cabin_class = first_segment.get("cabin", "economy").lower()

        return {
            "provider": "Amadeus",
            "carrier": carrier_name,
            "flight_number": f"{carrier_code}{first_segment.get('number', '000')}",
            "departure_airport": first_segment.get("departure", {}).get("iataCode", "UNK"),
            "arrival_airport": last_segment.get("arrival", {}).get("iataCode", "UNK"),
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration_minutes": duration_minutes,
            "stops": stops,
            "seat_class": cabin_class,
            "price_currency": price.get("currency", "KRW"),
            "price_amount": int(price_amount),
            "booking_url": "",  # Amadeus doesn't provide direct booking URLs
            "baggage_info": self._extract_baggage_info(offer),
        }

    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse ISO 8601 duration string to minutes (e.g., 'PT2H30M' -> 150)"""
        try:
            # Simple parser for PT format (e.g., PT2H30M, PT45M, PT1H)
            duration_str = duration_str.replace("PT", "")
            hours = 0
            minutes = 0

            if "H" in duration_str:
                parts = duration_str.split("H")
                hours = int(parts[0])
                duration_str = parts[1] if len(parts) > 1 else ""

            if "M" in duration_str and duration_str != "M":
                minutes = int(duration_str.replace("M", ""))

            return hours * 60 + minutes
        except Exception:
            return 0

    @staticmethod
    def _parse_datetime(dt_str: str | None) -> datetime:
        """
        Parse ISO datetime string and ensure timezone-aware datetime

        Amadeus API may return timestamps without timezone offset (e.g., "2024-11-03T10:45:00").
        We default to UTC to ensure compatibility with PostgreSQL DateTime(timezone=True) columns.
        """
        if not dt_str:
            return datetime.now(timezone.utc)
        try:
            # Amadeus uses ISO 8601 format: 2024-10-24T14:30:00 or 2024-10-24T14:30:00Z
            # Replace 'Z' with '+00:00' for proper ISO parsing
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

            # If the datetime is naive (no tzinfo), assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt
        except Exception:
            return datetime.now(timezone.utc)

    @staticmethod
    def _extract_baggage_info(offer: dict[str, Any]) -> dict[str, str]:
        """Extract baggage allowance information"""
        try:
            traveler_pricings = offer.get("travelerPricings", [])
            if not traveler_pricings:
                return {}

            # Get first traveler's baggage info
            fare_details = traveler_pricings[0].get("fareDetailsBySegment", [])
            if not fare_details:
                return {}

            included_bags = fare_details[0].get("includedCheckedBags", {})
            quantity = included_bags.get("quantity", 0)
            weight = included_bags.get("weight", 0)
            weight_unit = included_bags.get("weightUnit", "KG")

            return {
                "checked": f"{quantity}pc" if quantity else f"{weight}{weight_unit}",
                "carry_on": "7kg",  # Standard assumption
            }
        except Exception:
            return {"carry_on": "7kg", "checked": "23kg"}

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
        # base_return is kept for future round-trip logic
        _ = datetime.combine(return_date, datetime.min.time()).replace(tzinfo=timezone.utc)

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
                    "provider": "Amadeus",
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
                    "booking_url": "",
                    "baggage_info": {"carry_on": "7kg", "checked": "23kg"},
                }
            )

        return options


# Singleton helper
_amadeus_client: AmadeusClient | None = None


def get_amadeus_client() -> AmadeusClient:
    """Provide a singleton Amadeus client"""
    global _amadeus_client
    if _amadeus_client is None:
        _amadeus_client = AmadeusClient()
    return _amadeus_client
