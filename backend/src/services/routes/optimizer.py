"""Route optimization heuristics"""

from __future__ import annotations

import math
from typing import List

from ..ai.types import DailyItineraryDraft, RouteDraft


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371000  # meters
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


class RoutesOptimizer:
    """Build simple sequential routes between itinerary stops"""

    def build_routes(self, itinerary: DailyItineraryDraft) -> List[RouteDraft]:
        routes: List[RouteDraft] = []
        places = itinerary.places
        if len(places) < 2:
            return routes

        for current, nxt in zip(places, places[1:]):
            distance = _haversine_distance(
                current.place.latitude,
                current.place.longitude,
                nxt.place.latitude,
                nxt.place.longitude,
            )
            duration_minutes = max(int(distance / 80), 5)  # assume 4.8km/h walking baseline

            mode = "walking"
            if distance > 4000:
                mode = "public_transit"
            if distance > 15000:
                mode = "driving"

            routes.append(
                RouteDraft(
                    from_order=current.visit_order,
                    to_order=nxt.visit_order,
                    transport_mode=mode,
                    distance_meters=int(distance),
                    duration_minutes=duration_minutes,
                    estimated_cost=0 if mode == "walking" else 4000,
                )
            )

        return routes

