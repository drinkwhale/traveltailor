"""
Flight recommendation service
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.affiliate_tracker import affiliate_tracker
from ...core.cache import cache_flight_quote, get_cached_flight_quote
from ...integrations.amadeus import get_amadeus_client
from ...models.flight_option import FlightOption
from ...models.travel_plan import TravelPlan

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FlightRecommendationResult:
    """Return value for flight recommendation service"""

    origin_airport: str
    destination_airport: str
    options: list[FlightOption]


_AIRPORT_MAP: dict[str, str] = {
    "tokyo": "HND",
    "도쿄": "HND",
    "osaka": "KIX",
    "오사카": "KIX",
    "fukuoka": "FUK",
    "후쿠오카": "FUK",
    "sapporo": "CTS",
    "삿포로": "CTS",
    "hong kong": "HKG",
    "홍콩": "HKG",
    "singapore": "SIN",
    "싱가포르": "SIN",
    "seoul": "ICN",
    "서울": "GMP",
    "busan": "PUS",
    "부산": "PUS",
    "jeju": "CJU",
    "제주": "CJU",
    "new york": "JFK",
    "뉴욕": "JFK",
    "los angeles": "LAX",
    "la": "LAX",
    "paris": "CDG",
    "파리": "CDG",
    "london": "LHR",
    "런던": "LHR",
    "bangkok": "BKK",
    "방콕": "BKK",
}


class FlightRecommender:
    """Persist flight options for a travel plan"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.client = get_amadeus_client()

    async def get_recommendations(
        self,
        plan: TravelPlan,
        *,
        force_refresh: bool = False,
    ) -> FlightRecommendationResult:
        """Return flight options, generating them if needed"""
        origin = self._determine_origin(plan)
        destination = self._determine_destination(plan)
        cache_key = (
            f"{origin}:{destination}:{plan.start_date.isoformat()}:"
            f"{plan.end_date.isoformat()}:{plan.traveler_count}"
        )

        if force_refresh:
            await self._delete_existing(plan.id)
        else:
            cached_quote = await get_cached_flight_quote(cache_key)
            if cached_quote:
                existing = await self._fetch_existing(plan.id)
                if existing:
                    logger.info("Returning cached flight quote for %s", cache_key)
                    return FlightRecommendationResult(origin, destination, existing)

        existing = await self._fetch_existing(plan.id)
        if existing:
            return FlightRecommendationResult(origin, destination, existing)

        flights = await self.client.search_round_trip(
            origin=origin,
            destination=destination,
            departure_date=plan.start_date,
            return_date=plan.end_date,
            adults=max(plan.traveler_count, 1),
            cabin_class="economy",
        )

        if not flights:
            logger.info(
                "No flight recommendations for plan %s (%s -> %s)",
                plan.id,
                origin,
                destination,
            )
            return FlightRecommendationResult(origin, destination, [])

        options: list[FlightOption] = []
        for item in flights:
            booking_url = item.get("booking_url") or self._fallback_booking_url(
                origin,
                destination,
                plan.start_date,
                plan.end_date,
                plan.traveler_count,
            )
            tracked_url = affiliate_tracker.build_link(
                booking_url,
                extra={"provider": "amadeus"},
            )
            option = FlightOption(
                travel_plan_id=plan.id,
                provider=item.get("provider", "Amadeus"),
                carrier=item.get("carrier", "Unknown Carrier"),
                flight_number=item.get("flight_number", "XX000"),
                departure_airport=item.get("departure_airport", origin),
                arrival_airport=item.get("arrival_airport", destination),
                departure_time=item.get("departure_time"),
                arrival_time=item.get("arrival_time"),
                duration_minutes=int(item.get("duration_minutes") or 0) or 1,
                stops=int(item.get("stops") or 0),
                seat_class=item.get("seat_class"),
                baggage_info=item.get("baggage_info"),
                price_currency=item.get("price_currency", "KRW"),
                price_amount=int(item.get("price_amount") or 0),
                booking_url=tracked_url,
                affiliate_code=item.get("affiliate_code"),
            )
            self.session.add(option)
            options.append(option)

        await self.session.commit()
        for option in options:
            await self.session.refresh(option)

        cheapest = min(options, key=lambda opt: opt.price_amount, default=None)
        if cheapest:
            await cache_flight_quote(
                cache_key,
                {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": plan.start_date.isoformat(),
                    "return_date": plan.end_date.isoformat(),
                    "traveler_count": plan.traveler_count,
                    "currency": cheapest.price_currency,
                    "price_amount": cheapest.price_amount,
                    "provider": cheapest.provider,
                },
            )

        return FlightRecommendationResult(origin, destination, options)

    async def _fetch_existing(self, plan_id: UUID) -> list[FlightOption]:
        result = await self.session.execute(
            select(FlightOption)
            .where(FlightOption.travel_plan_id == plan_id)
            .order_by(FlightOption.price_amount.asc())
        )
        return list(result.scalars().all())

    async def _delete_existing(self, plan_id: UUID) -> None:
        await self.session.execute(
            delete(FlightOption).where(FlightOption.travel_plan_id == plan_id)
        )
        await self.session.commit()

    def _determine_origin(self, plan: TravelPlan) -> str:
        prefs = plan.preferences or {}
        origin = None
        if isinstance(prefs, dict):
            request = prefs.get("request")
            if isinstance(request, dict):
                origin = request.get("origin_airport") or request.get("home_airport")

        if not origin:
            origin = "ICN"
        return str(origin).upper()[:3]

    def _determine_destination(self, plan: TravelPlan) -> str:
        destination = plan.destination
        key = destination.lower()
        if key in _AIRPORT_MAP:
            return _AIRPORT_MAP[key]

        if plan.country:
            country_key = plan.country.lower()
            if country_key in _AIRPORT_MAP:
                return _AIRPORT_MAP[country_key]

        if len(destination) >= 3:
            return destination[:3].upper()
        return "NRT"

    def _fallback_booking_url(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date,
        travelers: int,
    ) -> str:
        # Amadeus doesn't provide direct booking URLs, so we use Google Flights as fallback
        return (
            "https://www.google.com/travel/flights/"
            f"?q=Flights%20from%20{origin}%20to%20{destination}%20on%20"
            f"{departure_date.isoformat()}%20through%20{return_date.isoformat()}"
        )
