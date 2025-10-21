"""
Generate branded travel itinerary PDFs from persisted plan data.
"""

from __future__ import annotations

import asyncio
import base64
import datetime as dt
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Sequence
from uuid import UUID

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...config.settings import settings
from ...integrations.mapbox import MapboxError, MapboxStaticClient, get_mapbox_static_client
from ...models.accommodation_option import AccommodationOption
from ...models.daily_itinerary import DailyItinerary
from ...models.flight_option import FlightOption
from ...models.itinerary_place import ItineraryPlace
from ...models.route import Route
from ...models.travel_plan import TravelPlan
from ...services.pdf import PdfRenderError, get_pdf_renderer
from .storage import PdfStorageError, SupabasePdfStorage


class PdfGenerationError(RuntimeError):
    """Base error for PDF generation failures."""


class PdfPlanNotFoundError(PdfGenerationError):
    """Raised when the target travel plan was not found."""


@dataclass(slots=True)
class PdfGenerationResult:
    """Result payload returned after generating the PDF."""

    file_name: str
    download_url: str
    storage_path: str
    expires_at: dt.datetime | None


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
    enable_async=False,
)
_template = _env.get_template("itinerary.html")
_styles = (TEMPLATES_DIR / "styles.css").read_text(encoding="utf-8")


def _load_logo_data_uri() -> str | None:
    logo_path = ASSETS_DIR / "logo.svg"
    if not logo_path.exists():
        return None
    payload = logo_path.read_bytes()
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


_logo_data_uri = _load_logo_data_uri()


def _slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    normalized = re.sub(r"[-\s]+", "-", normalized)
    slug = normalized.strip("-")
    return slug or "travel-itinerary"


def _format_currency(amount: int | None, currency: str = "KRW") -> str | None:
    if amount is None:
        return None
    return f"{amount:,.0f} {currency}"


def _format_duration(minutes: int | None) -> str | None:
    if minutes is None:
        return None
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}시간 {mins}분" if mins else f"{hours}시간"
    return f"{mins}분"


def _format_distance(meters: int | None) -> str | None:
    if meters is None:
        return None
    kilometres = meters / 1000
    if kilometres >= 1:
        return f"{kilometres:.1f} km"
    return f"{meters} m"


class _TransportLabel(str, Enum):
    walking = "도보"
    driving = "차량"
    public_transit = "대중교통"
    taxi = "택시"
    bicycle = "자전거"

    @classmethod
    def display(cls, mode: str) -> str:
        try:
            return cls(mode).value
        except ValueError:
            return mode.replace("_", " ").title()


class PdfGeneratorService:
    """Coordinates data gathering, rendering, and storage for itinerary PDFs."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        storage: SupabasePdfStorage | None = None,
        mapbox: MapboxStaticClient | None = None,
    ) -> None:
        self._session = session
        self._storage = storage or SupabasePdfStorage()
        self._mapbox: MapboxStaticClient | None
        if mapbox is not None:
            self._mapbox = mapbox
        else:
            try:
                self._mapbox = get_mapbox_static_client()
            except Exception:
                self._mapbox = None

    async def generate(self, plan_id: UUID, user_id: UUID) -> PdfGenerationResult:
        plan = await self._load_plan(plan_id, user_id)
        if plan is None:
            raise PdfPlanNotFoundError("Travel plan not found or access denied.")

        html = await self._render_html(plan)
        renderer = await get_pdf_renderer()
        try:
            pdf_bytes = await renderer.render(html)
        except PdfRenderError as exc:
            raise PdfGenerationError(str(exc)) from exc

        file_name = self._build_file_name(plan)
        try:
            stored = await self._storage.upload_pdf(plan.id, file_name, pdf_bytes)
        except PdfStorageError as exc:
            raise PdfGenerationError(str(exc)) from exc

        return PdfGenerationResult(
            file_name=file_name,
            download_url=stored.url,
            storage_path=stored.path,
            expires_at=stored.expires_at,
        )

    async def _load_plan(self, plan_id: UUID, user_id: UUID) -> TravelPlan | None:
        stmt = (
            select(TravelPlan)
            .where(TravelPlan.id == plan_id, TravelPlan.user_id == user_id)
            .options(
                selectinload(TravelPlan.daily_itineraries)
                .selectinload(DailyItinerary.itinerary_places)
                .selectinload(ItineraryPlace.place),
                selectinload(TravelPlan.daily_itineraries)
                .selectinload(DailyItinerary.routes)
                .selectinload(Route.from_place),
                selectinload(TravelPlan.daily_itineraries)
                .selectinload(DailyItinerary.routes)
                .selectinload(Route.to_place),
                selectinload(TravelPlan.flight_options),
                selectinload(TravelPlan.accommodation_options),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def _render_html(self, plan: TravelPlan) -> str:
        context = {
            "plan": await self._serialize_plan(plan),
            "brand": {
                "name": settings.PDF_BRAND_NAME,
                "logo_data_uri": _logo_data_uri,
            },
            "styles": _styles,
            "generated_at": dt.datetime.now(dt.timezone.utc),
        }
        return _template.render(**context)

    async def _serialize_plan(self, plan: TravelPlan) -> dict[str, Any]:
        day_coroutines = [
            self._serialize_day(daily)
            for daily in sorted(plan.daily_itineraries, key=lambda item: item.day_number)
        ]
        days = await asyncio.gather(*day_coroutines) if day_coroutines else []
        return {
            "id": str(plan.id),
            "title": plan.title,
            "destination": plan.destination,
            "country": plan.country,
            "start_date": plan.start_date,
            "end_date": plan.end_date,
            "total_days": plan.total_days,
            "total_nights": plan.total_nights,
            "budget_total": plan.budget_total,
            "budget_breakdown": dict(plan.budget_breakdown or {}),
            "traveler_type": plan.traveler_type,
            "traveler_count": plan.traveler_count,
            "ai_model_version": plan.ai_model_version,
            "days": days,
            "flights": [self._serialize_flight(option) for option in plan.flight_options],
            "accommodations": [
                self._serialize_accommodation(option) for option in plan.accommodation_options
            ],
        }

    async def _serialize_day(self, daily: DailyItinerary) -> dict[str, Any]:
        markers = sorted(daily.itinerary_places, key=lambda item: item.visit_order)
        routes = sorted(daily.routes, key=lambda item: item.from_order)
        map_image = None
        if markers and self._mapbox is not None:
            try:
                coordinates = [
                    (float(place.place.latitude), float(place.place.longitude)) for place in markers
                ]
                # Draw route using marker order so the map remains informative even without stored polylines.
                path: Sequence[tuple[float, float]] | None = coordinates if len(coordinates) > 1 else None
                image_bytes = await self._mapbox.get_static_map(markers=coordinates, path=path)
                if image_bytes:
                    map_image = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('ascii')}"
            except (MapboxError, ValueError, RuntimeError):
                map_image = None

        return {
            "day_number": daily.day_number,
            "date": daily.date,
            "theme": daily.theme,
            "notes": daily.notes,
            "map_image": map_image,
            "places": [self._serialize_place(place) for place in markers],
            "routes": [self._serialize_route(route) for route in routes],
        }

    def _serialize_place(self, visit: ItineraryPlace) -> dict[str, Any]:
        place = visit.place
        return {
            "name": place.name,
            "category": place.category,
            "address": place.address,
            "visit_order": visit.visit_order,
            "visit_time": visit.visit_time.isoformat(timespec="minutes") if visit.visit_time else None,
            "duration_minutes": visit.duration_minutes,
            "duration_label": _format_duration(visit.duration_minutes),
            "estimated_cost": visit.estimated_cost,
            "estimated_cost_label": _format_currency(visit.estimated_cost),
            "description": place.description or visit.ai_recommendation_reason,
            "visit_type": visit.visit_type,
        }

    def _serialize_route(self, route: Route) -> dict[str, Any]:
        instructions = []
        if route.instructions:
            for item in route.instructions:
                text = item.get("instruction") if isinstance(item, dict) else None
                if text:
                    instructions.append(text)
        return {
            "from_name": route.from_place.name if route.from_place else "출발",
            "to_name": route.to_place.name if route.to_place else "도착",
            "transport_mode": route.transport_mode,
            "transport_label": _TransportLabel.display(route.transport_mode),
            "duration_minutes": route.duration_minutes,
            "duration_label": _format_duration(route.duration_minutes),
            "distance_meters": route.distance_meters,
            "distance_label": _format_distance(route.distance_meters),
            "estimated_cost": route.estimated_cost,
            "estimated_cost_label": _format_currency(route.estimated_cost),
            "instructions": instructions,
        }

    def _serialize_flight(self, option: FlightOption) -> dict[str, Any]:
        return {
            "carrier": option.carrier,
            "flight_number": option.flight_number,
            "provider": option.provider,
            "departure_airport": option.departure_airport,
            "arrival_airport": option.arrival_airport,
            "departure_time": option.departure_time,
            "arrival_time": option.arrival_time,
            "duration_label": _format_duration(option.duration_minutes),
            "stops": option.stops,
            "seat_class": option.seat_class,
            "price_label": _format_currency(option.price_amount, option.price_currency),
            "booking_url": option.booking_url,
        }

    def _serialize_accommodation(self, option: AccommodationOption) -> dict[str, Any]:
        return {
            "name": option.name,
            "provider": option.provider,
            "address": option.address,
            "price_label": _format_currency(option.total_price, option.price_currency),
            "nights": option.nights,
            "check_in_date": option.check_in_date,
            "check_out_date": option.check_out_date,
            "rating": option.rating,
            "review_count": option.review_count,
            "booking_url": option.booking_url,
        }

    def _build_file_name(self, plan: TravelPlan) -> str:
        slug = _slugify(f"{plan.destination}-{plan.title}")
        start = plan.start_date.strftime("%Y%m%d")
        end = plan.end_date.strftime("%Y%m%d")
        return f"{slug}-{start}-{end}.pdf"
