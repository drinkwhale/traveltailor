"""
Geospatial helper utilities.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple


Coordinate = tuple[float, float]


def encode_polyline(coordinates: Sequence[Coordinate]) -> str:
    """Encode coordinates into a Google/Mapbox compatible polyline string."""
    result: list[str] = []
    prev_lat = 0
    prev_lng = 0

    for lat, lng in coordinates:
        lat_i = int(round(lat * 1e5))
        lng_i = int(round(lng * 1e5))

        d_lat = lat_i - prev_lat
        d_lng = lng_i - prev_lng

        prev_lat = lat_i
        prev_lng = lng_i

        result.append(_encode_value(d_lat))
        result.append(_encode_value(d_lng))

    return "".join(result)


def _encode_value(value: int) -> str:
    value <<= 1
    if value < 0:
        value = ~value

    encoded = ""
    while value >= 0x20:
        encoded += chr((0x20 | (value & 0x1F)) + 63)
        value >>= 5
    encoded += chr(value + 63)
    return encoded


def haversine_distance_meters(
    src: Coordinate,
    dest: Coordinate,
    radius: float = 6_371_000,
) -> float:
    """Approximate distance between two coordinates."""
    lat1, lon1 = src
    lat2, lon2 = dest
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def calculate_bounds(coordinates: Iterable[Coordinate]) -> tuple[Coordinate, Coordinate]:
    """Calculate southwest and northeast bounds for the coordinate collection."""
    latitudes: list[float] = []
    longitudes: list[float] = []

    for lat, lng in coordinates:
        latitudes.append(lat)
        longitudes.append(lng)

    if not latitudes or not longitudes:
        raise ValueError("At least one coordinate is required to compute bounds.")

    sw = (min(latitudes), min(longitudes))
    ne = (max(latitudes), max(longitudes))
    return sw, ne
