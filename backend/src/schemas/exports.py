"""
Schemas for map export responses.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from .itinerary import TransportMode


class MapCoordinate(BaseModel):
    latitude: float
    longitude: float


class MapBounds(BaseModel):
    southwest: MapCoordinate
    northeast: MapCoordinate


class MapMarker(BaseModel):
    id: UUID
    place_id: UUID
    name: str
    order: int
    latitude: float
    longitude: float
    category: str
    visit_time: str | None = None
    address: str | None = None


class MapRouteStep(BaseModel):
    instruction: str
    distance_meters: float
    duration_seconds: float


class MapRoute(BaseModel):
    id: UUID
    from_place_id: UUID
    to_place_id: UUID
    from_order: int
    to_order: int
    transport_mode: TransportMode
    distance_meters: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=0)
    polyline: str
    summary: str | None = None
    steps: list[MapRouteStep] = Field(default_factory=list)


class MapDaySummary(BaseModel):
    total_distance_meters: int = Field(default=0, ge=0)
    total_duration_minutes: int = Field(default=0, ge=0)


class MapLink(BaseModel):
    web: str
    mobile: str | None = None


class MapExportLinks(BaseModel):
    google_maps: MapLink
    kakao_map: MapLink


class MapDay(BaseModel):
    day_number: int
    date: date
    theme: str | None = None
    markers: list[MapMarker]
    routes: list[MapRoute]
    summary: MapDaySummary
    export_links: MapExportLinks


class MapExportPlan(BaseModel):
    id: UUID
    title: str
    destination: str
    start_date: date
    end_date: date


class MapExportResponse(BaseModel):
    plan: MapExportPlan
    bounds: MapBounds
    days: list[MapDay]
