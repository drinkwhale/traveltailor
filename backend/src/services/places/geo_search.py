"""Geo-spatial search utilities for nearby places."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

from sqlalchemy import Float, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.place import Place


@dataclass(slots=True)
class GeoSearchParams:
    latitude: float
    longitude: float
    radius_km: float = 5.0
    limit: int = 20
    category: str | None = None


class GeoSearchService:
    """Provide distance ordered place search leveraging PostGIS functions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self, params: GeoSearchParams) -> Select:
        target_point = func.ST_SetSRID(func.ST_MakePoint(params.longitude, params.latitude), 4326)
        place_point = func.ST_SetSRID(
            func.ST_MakePoint(
                func.cast(Place.longitude, Float),
                func.cast(Place.latitude, Float),
            ),
            4326,
        )

        distance = func.ST_DistanceSphere(place_point, target_point).label("distance")

        query = (
            select(Place, distance)
            .where(
                func.ST_DWithin(
                    place_point.cast("geography"),
                    target_point.cast("geography"),
                    params.radius_km * 1000,
                )
            )
            .order_by(distance)
            .limit(params.limit)
        )

        if params.category:
            query = query.where(Place.category == params.category)

        return query

    async def search(self, params: GeoSearchParams) -> list[tuple[Place, float]]:
        """Return places ordered by distance from the provided coordinate."""

        result = await self.session.execute(self._base_query(params))
        rows: Sequence[tuple[Place, float]] = result.all()
        return list(rows)

    async def nearby_activities(self, params: GeoSearchParams) -> list[tuple[Place, float]]:
        return await self.search(replace(params, category="attraction"))

    async def nearby_restaurants(self, params: GeoSearchParams) -> list[tuple[Place, float]]:
        return await self.search(replace(params, category="restaurant"))
