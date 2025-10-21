"""Travel plan orchestration service"""

from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.settings import settings
from ...models.daily_itinerary import DailyItinerary
from ...models.itinerary_place import ItineraryPlace
from ...models.place import Place
from ...models.route import Route
from ...models.travel_plan import TravelPlan
from ...models.user_preference import UserPreference
from ...schemas.place import ItineraryPlaceSummary, PlaceCreate
from ...schemas.travel_plan import BudgetBreakdown, TravelPlanCreate, TravelPlanResponse
from ...schemas.itinerary import DailyItineraryResponse, RouteResponse
from ..places.recommender import PlacesRecommender
from .budget_allocator import BudgetAllocator, BudgetAllocationResult
from .cache import AIResponseCache, cache
from .preference_analyzer import AnalyzedPreferences, PreferenceAnalyzer
from .timeline_generator import TimelineGenerator
from .types import DailyItineraryDraft, TravelPlanDraft


class TravelPlanner:
    """Coordinates AI helpers to generate a full travel plan"""

    def __init__(
        self,
        session: AsyncSession,
        *,
        cache_backend: AIResponseCache = cache,
    ) -> None:
        self.session = session
        self.cache = cache_backend
        self.preference_analyzer = PreferenceAnalyzer()
        self.budget_allocator = BudgetAllocator()
        self.timeline_generator = TimelineGenerator()
        self.recommender = PlacesRecommender()

    async def _load_user_preference(self, user_id: UUID) -> UserPreference | None:
        result = await self.session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_or_create_place(
        self,
        place_data: PlaceCreate,
        cache_map: dict[str, Place],
    ) -> Place:
        key = place_data.external_id or f"{place_data.name}:{place_data.latitude}:{place_data.longitude}"
        if key in cache_map:
            return cache_map[key]

        existing: Place | None = None
        if place_data.external_id:
            result = await self.session.execute(
                select(Place).where(Place.external_id == place_data.external_id)
            )
            existing = result.scalar_one_or_none()

        if existing:
            cache_map[key] = existing
            return existing

        new_place = Place(
            external_id=place_data.external_id,
            external_source=place_data.external_source,
            name=place_data.name,
            category=place_data.category,
            subcategory=place_data.subcategory,
            address=place_data.address,
            city=place_data.city,
            country=place_data.country,
            latitude=place_data.latitude,
            longitude=place_data.longitude,
            rating=place_data.rating,
            price_level=place_data.price_level,
            phone=place_data.phone,
            website=place_data.website,
            opening_hours=place_data.opening_hours,
            photos=place_data.photos,
            description=place_data.description,
            tags=place_data.tags,
        )
        self.session.add(new_place)
        await self.session.flush()
        cache_map[key] = new_place
        return new_place

    async def _persist_daily_itinerary(
        self,
        plan: TravelPlan,
        draft: DailyItineraryDraft,
        place_cache: dict[str, Place],
    ) -> DailyItinerary:
        daily = DailyItinerary(
            travel_plan_id=plan.id,
            date=draft.date,
            day_number=draft.day_number,
            theme=draft.theme,
            notes=draft.notes,
            weather_forecast=draft.weather_forecast,
        )
        self.session.add(daily)
        await self.session.flush()

        order_to_place_id: dict[int, UUID] = {}

        for place_draft in draft.places:
            place_model = await self._get_or_create_place(place_draft.place, place_cache)
            itinerary_place = ItineraryPlace(
                daily_itinerary_id=daily.id,
                place_id=place_model.id,
                visit_order=place_draft.visit_order,
                visit_time=place_draft.visit_time,
                duration_minutes=place_draft.duration_minutes,
                visit_type=place_draft.visit_type,
                estimated_cost=place_draft.estimated_cost,
                ai_recommendation_reason=place_draft.ai_recommendation_reason,
                user_notes=place_draft.user_notes,
            )
            self.session.add(itinerary_place)
            await self.session.flush()
            order_to_place_id[place_draft.visit_order] = place_model.id

        for route_draft in draft.routes:
            from_place_id = order_to_place_id.get(route_draft.from_order)
            to_place_id = order_to_place_id.get(route_draft.to_order)
            if not from_place_id or not to_place_id:
                continue

            route = Route(
                daily_itinerary_id=daily.id,
                from_place_id=from_place_id,
                to_place_id=to_place_id,
                from_order=route_draft.from_order,
                to_order=route_draft.to_order,
                transport_mode=route_draft.transport_mode,
                distance_meters=route_draft.distance_meters,
                duration_minutes=route_draft.duration_minutes,
                estimated_cost=route_draft.estimated_cost,
                route_polyline=route_draft.route_polyline,
                instructions=route_draft.instructions,
            )
            self.session.add(route)

        return daily

    async def generate_plan(
        self,
        user_id: UUID,
        payload: TravelPlanCreate,
    ) -> TravelPlan:
        start = perf_counter()
        stored_pref = await self._load_user_preference(user_id)

        cache_payload = {
            "user_id": str(user_id),
            "plan": payload.model_dump(mode="json"),
        }
        cache_key = self.cache.build_key(cache_payload)
        cached = await self.cache.get(cache_key)

        if cached:
            analyzed = AnalyzedPreferences(**cached["analyzed"])
            budget_result = BudgetAllocationResult(
                breakdown=BudgetBreakdown(**cached["budget"]["breakdown"]),
                per_day=cached["budget"]["per_day"],
                warnings=cached["budget"].get("warnings", []),
            )
        else:
            analyzed = self.preference_analyzer.analyze(payload, stored_pref)
            total_days = (payload.end_date - payload.start_date).days + 1
            budget_result = self.budget_allocator.allocate(
                payload.budget_total,
                total_days,
                analyzed,
            )
            await self.cache.set(
                cache_key,
                {
                    "analyzed": analyzed.to_dict(),
                    "budget": budget_result.to_dict(),
                },
            )

        bundle = await self.recommender.recommend(payload, analyzed)
        warnings = list(budget_result.warnings)
        warnings.extend(bundle.warnings)

        total_days = (payload.end_date - payload.start_date).days + 1
        total_nights = max(total_days - 1, 0)
        draft = TravelPlanDraft(
            title=payload.title or f"{payload.destination} {total_days}일 일정",
            destination=payload.destination,
            country=payload.country,
            start_date=payload.start_date,
            end_date=payload.end_date,
            total_days=total_days,
            total_nights=total_nights,
            budget_total=payload.budget_total,
            traveler_type=payload.traveler_type,
            traveler_count=payload.traveler_count,
            preferences=payload.preferences,
            budget_breakdown=budget_result.breakdown,
            ai_model_version=getattr(settings, "OPENAI_MODEL", "heuristic-v1"),
        )

        self.timeline_generator.build_daily_itineraries(
            payload,
            draft,
            bundle,
            analyzed,
            budget_result,
        )

        plan = TravelPlan(
            user_id=user_id,
            title=draft.title,
            destination=draft.destination,
            country=draft.country,
            start_date=draft.start_date,
            end_date=draft.end_date,
            total_days=draft.total_days,
            total_nights=draft.total_nights,
            budget_total=draft.budget_total,
            budget_allocated=budget_result.breakdown.total,
            budget_breakdown=draft.budget_breakdown.model_dump(),
            traveler_type=draft.traveler_type,
            traveler_count=draft.traveler_count,
            preferences={
                "request": payload.preferences.model_dump(mode="json"),
                "analysis": analyzed.to_dict(),
                "warnings": warnings,
            },
            status="in_progress",
            ai_model_version=draft.ai_model_version,
        )

        self.session.add(plan)
        await self.session.flush()

        place_cache: dict[str, Place] = {}
        for daily_draft in draft.daily_itineraries:
            await self._persist_daily_itinerary(plan, daily_draft, place_cache)

        plan.status = "completed"
        plan.generation_time_seconds = round(perf_counter() - start, 2)

        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def build_response(self, plan: TravelPlan) -> TravelPlanResponse:
        await self.session.refresh(plan, attribute_names=["daily_itineraries"])

        daily_responses: list[DailyItineraryResponse] = []
        for daily in plan.daily_itineraries:
            places: list[ItineraryPlaceSummary] = []
            for visit in daily.itinerary_places:
                places.append(
                    ItineraryPlaceSummary(
                        id=visit.id,
                        place_id=visit.place_id,
                        name=visit.place.name,
                        category=visit.place.category,  # type: ignore[arg-type]
                        latitude=float(visit.place.latitude),
                        longitude=float(visit.place.longitude),
                        visit_order=visit.visit_order,
                        visit_type=visit.visit_type,  # type: ignore[arg-type]
                        visit_time=visit.visit_time,
                        duration_minutes=visit.duration_minutes,
                        estimated_cost=visit.estimated_cost,
                        ai_recommendation_reason=visit.ai_recommendation_reason,
                        user_notes=visit.user_notes,
                        is_confirmed=visit.is_confirmed,
                    )
                )

            routes: list[RouteResponse] = []
            for route in daily.routes:
                routes.append(
                    RouteResponse(
                        id=route.id,
                        daily_itinerary_id=route.daily_itinerary_id,
                        from_place_id=route.from_place_id,
                        to_place_id=route.to_place_id,
                        from_order=route.from_order,
                        to_order=route.to_order,
                        transport_mode=route.transport_mode,  # type: ignore[arg-type]
                        distance_meters=route.distance_meters,
                        duration_minutes=route.duration_minutes,
                        estimated_cost=route.estimated_cost,
                        route_polyline=route.route_polyline,
                        instructions=route.instructions,
                    )
                )

            daily_responses.append(
                DailyItineraryResponse(
                    id=daily.id,
                    travel_plan_id=daily.travel_plan_id,
                    date=daily.date,
                    day_number=daily.day_number,
                    theme=daily.theme,
                    notes=daily.notes,
                    weather_forecast=daily.weather_forecast,
                    places=places,
                    routes=routes,
                )
            )

        response = TravelPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            title=plan.title,
            destination=plan.destination,
            country=plan.country,
            start_date=plan.start_date,
            end_date=plan.end_date,
            total_days=plan.total_days,
            total_nights=plan.total_nights,
            budget_total=plan.budget_total,
            budget_allocated=plan.budget_allocated,
            budget_breakdown=BudgetBreakdown(**plan.budget_breakdown)
            if plan.budget_breakdown
            else None,
            traveler_type=plan.traveler_type,
            traveler_count=plan.traveler_count,
            preferences=plan.preferences,
            status=plan.status,  # type: ignore[arg-type]
            ai_model_version=plan.ai_model_version,
            generation_time_seconds=float(plan.generation_time_seconds or 0),
            created_at=plan.created_at.isoformat(),
            updated_at=plan.updated_at.isoformat(),
            daily_itineraries=daily_responses,
        )
        return response
