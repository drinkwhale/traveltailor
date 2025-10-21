"""
Mapbox Directions API integration.

Provides a thin async client for requesting routes between coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import httpx

from ..config import settings


class MapboxError(Exception):
    """Raised when Mapbox responds with an error."""


@dataclass(slots=True)
class MapboxStep:
    """Individual navigational step returned by Mapbox."""

    instruction: str
    distance_meters: float
    duration_seconds: float


@dataclass(slots=True)
class MapboxRoute:
    """Simplified directions payload."""

    distance_meters: float
    duration_seconds: float
    coordinates: list[tuple[float, float]]
    summary: str | None
    steps: list[MapboxStep]


class MapboxClient:
    """Async Mapbox Directions client."""

    _BASE_URL = "https://api.mapbox.com/directions/v5"

    def __init__(self, timeout: float = 30.0) -> None:
        token = settings.MAPBOX_ACCESS_TOKEN
        if not token:
            raise ValueError("MAPBOX_ACCESS_TOKEN is not configured.")
        self._token = token
        self._client = httpx.AsyncClient(base_url=self._BASE_URL, timeout=timeout)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def get_directions(
        self,
        coordinates: Sequence[tuple[float, float]],
        profile: str = "driving",
        *,
        language: str = "ko",
        steps: bool = True,
    ) -> MapboxRoute:
        """Request a directions route for the supplied coordinates.

        Args:
            coordinates: Sequence of (latitude, longitude) tuples.
            profile: Mapbox routing profile (driving, walking, cycling).
            language: Response language.
            steps: Whether to request step-by-step instructions.
        """
        if len(coordinates) < 2:
            raise ValueError("At least two coordinates are required to request a route.")

        coordinate_path = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in coordinates)
        params: dict[str, Any] = {
            "access_token": self._token,
            "geometries": "geojson",
            "overview": "full",
            "language": language,
        }
        if steps:
            params["steps"] = "true"

        response = await self._client.get(f"/mapbox/{profile}/{coordinate_path}", params=params)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - thin wrapper
            raise MapboxError(f"Mapbox request failed: {exc}") from exc

        data = response.json()
        routes = data.get("routes") or []
        if not routes:
            raise MapboxError("Mapbox returned no routes for the supplied coordinates.")

        primary = routes[0]
        geometry = primary.get("geometry", {})
        geo_coordinates = geometry.get("coordinates") or []
        if not geo_coordinates:
            raise MapboxError("Mapbox response did not include route geometry.")

        # Convert [lon, lat] to (lat, lon)
        coordinates_ll = [(float(latlon[1]), float(latlon[0])) for latlon in geo_coordinates]

        steps_payload: list[MapboxStep] = []
        if steps and primary.get("legs"):
            for leg in primary["legs"]:
                for step in leg.get("steps", []):
                    maneuver = step.get("maneuver") or {}
                    instruction = maneuver.get("instruction") or ""
                    steps_payload.append(
                        MapboxStep(
                            instruction=instruction,
                            distance_meters=float(step.get("distance") or 0),
                            duration_seconds=float(step.get("duration") or 0),
                        )
                    )

        return MapboxRoute(
            distance_meters=float(primary.get("distance") or 0),
            duration_seconds=float(primary.get("duration") or 0),
            coordinates=coordinates_ll,
            summary=primary.get("summary"),
            steps=steps_payload,
        )


_mapbox_client: MapboxClient | None = None


def get_mapbox_client() -> MapboxClient:
    """Return a process-wide Mapbox client instance."""
    global _mapbox_client
    if _mapbox_client is None:
        _mapbox_client = MapboxClient()
    return _mapbox_client
