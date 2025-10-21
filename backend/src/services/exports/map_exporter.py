"""
Utilities for constructing map export payloads.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Sequence, cast
from uuid import UUID
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.geo_utils import (
    calculate_bounds,
    encode_polyline,
    haversine_distance_meters,
)
from ...integrations.mapbox import (
    MapboxClient,
    MapboxError,
    get_mapbox_client,
)
from ...models.daily_itinerary import DailyItinerary
from ...models.itinerary_place import ItineraryPlace
from ...models.route import Route
from ...models.travel_plan import TravelPlan
from ...schemas.exports import (
    MapBounds,
    MapCoordinate,
    MapDay,
    MapDaySummary,
    MapExportLinks,
    MapExportPlan,
    MapExportResponse,
    MapLink,
    MapMarker,
    MapRoute,
    MapRouteStep,
)
from ...schemas.itinerary import TransportMode


class MapExportError(Exception):
    """Base error for map exports."""


class MapExportNotFoundError(MapExportError):
    """Raised when a plan cannot be located."""


TransportProfile = {
    "walking": "walking",
    "driving": "driving",
    "public_transit": "driving",
    "taxi": "driving",
    "bicycle": "cycling",
}

GoogleTravelModes = {
    "walking": "walking",
    "driving": "driving",
    "taxi": "driving",
    "public_transit": "transit",
    "bicycle": "bicycling",
}

KakaoTravelModes = {
    "walking": "FOOT",
    "driving": "CAR",
    "taxi": "CAR",
    "public_transit": "PUBLICTRANSIT",
    "bicycle": "BICYCLE",
}


class MapExportService:
    """Build map export responses for travel plans."""

    def __init__(self, session: AsyncSession, mapbox_client: MapboxClient | None = None) -> None:
        self._session = session
        if mapbox_client is not None:
            self._mapbox = mapbox_client
        else:
            try:
                self._mapbox = get_mapbox_client()
            except Exception:
                self._mapbox = None

    async def build_map_export(self, plan_id: UUID, user_id: UUID) -> MapExportResponse:
        plan = await self._load_plan(plan_id, user_id)
        if plan is None:
            raise MapExportNotFoundError("Travel plan not found.")

        all_coordinates: list[tuple[float, float]] = []
        day_payloads: list[MapDay] = []

        for daily in sorted(plan.daily_itineraries, key=lambda d: d.day_number):
            day = await self._build_day_payload(daily)
            day_payloads.append(day)
            for marker in day.markers:
                all_coordinates.append((marker.latitude, marker.longitude))

        if not all_coordinates:
            raise MapExportError("Travel plan does not contain any locations to map.")

        sw, ne = calculate_bounds(all_coordinates)
        bounds = MapBounds(
            southwest=MapCoordinate(latitude=sw[0], longitude=sw[1]),
            northeast=MapCoordinate(latitude=ne[0], longitude=ne[1]),
        )

        plan_summary = MapExportPlan(
            id=plan.id,
            title=plan.title,
            destination=plan.destination,
            start_date=plan.start_date,
            end_date=plan.end_date,
        )

        return MapExportResponse(plan=plan_summary, bounds=bounds, days=day_payloads)

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
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().unique().one_or_none()

    async def _build_day_payload(self, daily: DailyItinerary) -> MapDay:
        markers = self._build_markers(daily)
        routes, day_summary = await self._build_routes(daily, markers)
        export_links = self._build_export_links(markers, routes)
        return MapDay(
            day_number=daily.day_number,
            date=daily.date,
            theme=daily.theme,
            markers=markers,
            routes=routes,
            summary=day_summary,
            export_links=export_links,
        )

    def _build_markers(self, daily: DailyItinerary) -> list[MapMarker]:
        markers: list[MapMarker] = []
        for visit in sorted(daily.itinerary_places, key=lambda item: item.visit_order):
            place = visit.place
            markers.append(
                MapMarker(
                    id=visit.id,
                    place_id=visit.place_id,
                    name=place.name,
                    order=visit.visit_order,
                    latitude=float(place.latitude),
                    longitude=float(place.longitude),
                    category=place.category or "unknown",
                    visit_time=visit.visit_time.isoformat() if visit.visit_time else None,
                    address=place.address,
                )
            )
        return markers

    async def _build_routes(
        self,
        daily: DailyItinerary,
        markers: Sequence[MapMarker],
    ) -> tuple[list[MapRoute], MapDaySummary]:
        marker_lookup = {marker.place_id: marker for marker in markers}
        routes: list[MapRoute] = []
        total_distance = 0
        total_duration = 0

        for route in sorted(daily.routes, key=lambda item: item.from_order):
            payload = await self._build_route_payload(route, marker_lookup)
            routes.append(payload)
            if payload.distance_meters is not None:
                total_distance += payload.distance_meters
            else:
                start = marker_lookup.get(route.from_place_id)
                end = marker_lookup.get(route.to_place_id)
                if start and end:
                    total_distance += int(
                        round(haversine_distance_meters((start.latitude, start.longitude), (end.latitude, end.longitude)))
                    )
            if payload.duration_minutes is not None:
                total_duration += payload.duration_minutes

        return routes, MapDaySummary(total_distance_meters=total_distance, total_duration_minutes=total_duration)

    async def _build_route_payload(
        self,
        route: Route,
        markers: dict[UUID, MapMarker],
    ) -> MapRoute:
        start = route.from_place
        end = route.to_place
        start_coord = (float(start.latitude), float(start.longitude))
        end_coord = (float(end.latitude), float(end.longitude))

        polyline = encode_polyline((start_coord, end_coord))
        steps: list[MapRouteStep] = []
        distance = route.distance_meters
        duration = route.duration_minutes
        summary: str | None = None

        if self._mapbox is not None:
            profile = TransportProfile.get(route.transport_mode, "driving")
            try:
                mapbox_route = await self._mapbox.get_directions(
                    (start_coord, end_coord),
                    profile=profile,
                )
                polyline = encode_polyline(mapbox_route.coordinates)
                steps = [
                    MapRouteStep(
                        instruction=step.instruction,
                        distance_meters=step.distance_meters,
                        duration_seconds=step.duration_seconds,
                    )
                    for step in mapbox_route.steps
                ]
                distance = int(round(mapbox_route.distance_meters))
                duration = int(math.ceil(mapbox_route.duration_seconds / 60)) or 1
                summary = mapbox_route.summary
            except (MapboxError, ValueError):
                pass

        if distance is None:
            distance = int(
                round(
                    haversine_distance_meters(
                        (start.latitude, start.longitude),
                        (end.latitude, end.longitude),
                    )
                )
            )
        if duration is None:
            duration = max(int(distance / 80), 5) if distance else 5

        return MapRoute(
            id=route.id,
            from_place_id=route.from_place_id,
            to_place_id=route.to_place_id,
            from_order=route.from_order,
            to_order=route.to_order,
            transport_mode=cast("TransportMode", route.transport_mode),
            distance_meters=distance,
            duration_minutes=duration,
            polyline=polyline,
            summary=summary,
            steps=steps,
        )

    def _build_export_links(
        self,
        markers: Sequence[MapMarker],
        routes: Sequence[MapRoute],
    ) -> MapExportLinks:
        google_mode = self._dominant_mode(routes)
        kakao_mode = google_mode

        google_link = self._build_google_link(markers, google_mode)
        kakao_link = self._build_kakao_link(markers, kakao_mode)
        return MapExportLinks(google_maps=google_link, kakao_map=kakao_link)

    def _build_google_link(self, markers: Sequence[MapMarker], mode: str) -> MapLink:
        if not markers:
            return MapLink(web="https://www.google.com/maps", mobile=None)

        origin = markers[0]
        destination = markers[-1]
        waypoints = markers[1:-1]

        travel_mode = GoogleTravelModes.get(mode, "driving")
        params = [
            ("api", "1"),
            ("origin", f"{origin.latitude:.6f},{origin.longitude:.6f}"),
            ("destination", f"{destination.latitude:.6f},{destination.longitude:.6f}"),
            ("travelmode", travel_mode),
        ]
        if waypoints:
            waypoint_value = "|".join(f"{wp.latitude:.6f},{wp.longitude:.6f}" for wp in waypoints)
            params.append(("waypoints", waypoint_value))

        query = "&".join(f"{key}={quote(value, safe=',|')}" for key, value in params)
        url = f"https://www.google.com/maps/dir/?{query}"
        return MapLink(web=url, mobile=url)

    def _build_kakao_link(self, markers: Sequence[MapMarker], mode: str) -> MapLink:
        if not markers:
            return MapLink(web="https://map.kakao.com", mobile=None)

        kakao_mode = KakaoTravelModes.get(mode, "CAR")
        origin = markers[0]
        destination = markers[-1]

        route_segments = [
            quote(f"{marker.name},{marker.latitude:.6f},{marker.longitude:.6f}", safe=",")
            for marker in markers
        ]
        web_url = f"https://map.kakao.com/link/route/{'/'.join(route_segments)}"
        mobile_url = (
            f"kakaomap://route?sp={origin.latitude:.6f},{origin.longitude:.6f}"
            f"&ep={destination.latitude:.6f},{destination.longitude:.6f}"
            f"&by={kakao_mode}"
        )
        return MapLink(web=web_url, mobile=mobile_url)

    def _dominant_mode(self, routes: Sequence[MapRoute]) -> str:
        if not routes:
            return "driving"
        counter = Counter(route.transport_mode for route in routes)
        return counter.most_common(1)[0][0]
