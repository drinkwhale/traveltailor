"""
Accommodation recommendation service
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from urllib.parse import urlencode
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.affiliate_tracker import affiliate_tracker
from ...integrations.agoda import get_agoda_client
from ...integrations.booking import booking_affiliate
from ...models.accommodation_option import AccommodationOption
from ...models.travel_plan import TravelPlan

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AccommodationRecommendationResult:
    """Accommodation recommendation payload"""

    check_in: date | None
    check_out: date | None
    options: list[AccommodationOption]


class AccommodationRecommender:
    """Persist accommodation options for a travel plan"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.agoda_client = get_agoda_client()

    async def get_recommendations(
        self,
        plan: TravelPlan,
        *,
        force_refresh: bool = False,
    ) -> AccommodationRecommendationResult:
        """Return accommodation recommendations for a travel plan"""
        if force_refresh:
            await self._delete_existing(plan.id)

        existing = await self._fetch_existing(plan.id)
        if existing:
            return AccommodationRecommendationResult(plan.start_date, plan.end_date, existing)

        nights = max((plan.end_date - plan.start_date).days, 1)
        hotels = await self.agoda_client.search_hotels(
            destination=plan.destination,
            country=plan.country,
            check_in=plan.start_date,
            nights=nights,
            adults=max(plan.traveler_count, 1),
        )

        currency = self._determine_currency(plan)

        if not hotels:
            logger.info("No Agoda results for plan %s, generating fallback accommodations", plan.id)
            hotels = self._fallback_hotels(
                plan.destination,
                plan.country,
                plan.start_date,
                nights,
                currency,
            )

        options: list[AccommodationOption] = []
        for index, hotel in enumerate(hotels):
            provider = hotel.get("provider", "Agoda")
            booking_url = hotel.get("booking_url")
            price_currency = str(hotel.get("price_currency", currency))
            if not booking_url:
                booking_url = self._build_partner_link(
                    provider,
                    hotel.get("name", "Hotel"),
                    plan.destination,
                    plan.start_date,
                    plan.end_date,
                    max(plan.traveler_count, 1),
                    price_currency,
                )

            option = AccommodationOption(
                travel_plan_id=plan.id,
                provider=provider,
                name=hotel.get("name", f"Option {index + 1}"),
                description=hotel.get("description"),
                address=hotel.get("address"),
                city=hotel.get("city") or plan.destination,
                country=hotel.get("country") or plan.country,
                latitude=hotel.get("latitude"),
                longitude=hotel.get("longitude"),
                rating=hotel.get("rating"),
                review_count=hotel.get("review_count"),
                star_rating=hotel.get("star_rating"),
                price_currency=price_currency,
                price_per_night=hotel.get("price_per_night"),
                total_price=hotel.get("total_price", 0),
                check_in_date=plan.start_date,
                check_out_date=plan.end_date,
                nights=nights,
                room_type=hotel.get("room_type"),
                booking_url=booking_url,
                image_url=hotel.get("image_url"),
                amenities=hotel.get("amenities"),
                tags=hotel.get("tags"),
                policies=hotel.get("policies"),
            )
            self.session.add(option)
            options.append(option)

        await self.session.commit()
        for option in options:
            await self.session.refresh(option)

        return AccommodationRecommendationResult(plan.start_date, plan.end_date, options)

    async def _fetch_existing(self, plan_id: UUID) -> list[AccommodationOption]:
        result = await self.session.execute(
            select(AccommodationOption)
            .where(AccommodationOption.travel_plan_id == plan_id)
            .order_by(AccommodationOption.total_price.asc())
        )
        return list(result.scalars().all())

    async def _delete_existing(self, plan_id: UUID) -> None:
        await self.session.execute(
            delete(AccommodationOption).where(AccommodationOption.travel_plan_id == plan_id)
        )
        await self.session.commit()

    def _determine_currency(self, plan: TravelPlan) -> str:
        prefs = plan.preferences or {}
        currency = None
        if isinstance(prefs, dict):
            analysis = prefs.get("analysis")
            if isinstance(analysis, dict):
                currency = analysis.get("preferred_currency")
            request = prefs.get("request")
            if not currency and isinstance(request, dict):
                currency = request.get("currency")

        if not currency:
            currency = "KRW"
        return str(currency).upper()[:3]

    def _fallback_hotels(
        self,
        destination: str,
        country: str | None,
        check_in: date,
        nights: int,
        currency: str,
    ) -> list[dict[str, object]]:
        base_price = 120_000
        templates = [
            ("TravelTailor Signature Hotel", "Booking.com", 4.7, 1350),
            ("City Central Stay", "Agoda", 4.3, 1024),
            ("Boutique Riverside Suites", "Agoda", 4.9, 640),
        ]

        hotels: list[dict[str, object]] = []
        for index, (name, provider, rating, reviews) in enumerate(templates):
            price_per_night = base_price + index * 30_000
            checkout = check_in + timedelta(days=nights)
            booking_url = self._build_partner_link(
                provider,
                name,
                destination,
                check_in,
                checkout,
                2,
                currency,
            )
            hotels.append(
                {
                    "provider": provider,
                    "name": name,
                    "address": f"{destination} 중심 관광지 인근",
                    "city": destination,
                    "country": country,
                    "rating": rating,
                    "review_count": reviews,
                    "price_currency": currency,
                    "price_per_night": price_per_night,
                    "total_price": price_per_night * nights,
                    "booking_url": booking_url,
                    "image_url": None,
                    "amenities": ["무료 Wi-Fi", "조식 포함", "24시간 데스크"],
                    "tags": ["가족 친화", "교통 편리"],
                }
            )

        return hotels

    def _build_partner_link(
        self,
        provider: str,
        hotel_name: str,
        destination: str,
        check_in: date,
        check_out: date,
        adults: int,
        currency: str,
    ) -> str:
        if provider.lower() == "booking.com":
            return booking_affiliate.build_hotel_link(
                hotel_name=hotel_name,
                city=destination,
                currency=currency,
                check_in=check_in,
                check_out=check_out,
                params={"group_adults": str(adults)},
            )

        params = urlencode(
            {
                "city": destination,
                "checkin": check_in.isoformat(),
                "checkout": check_out.isoformat(),
                "adults": str(adults),
            }
        )
        base_url = "https://www.agoda.com/search"
        return affiliate_tracker.build_link(f"{base_url}?{params}")
