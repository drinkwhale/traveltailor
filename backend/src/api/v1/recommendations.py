"""
Recommendation API endpoints
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_db
from ...core.security import get_current_user_id
from ...models.travel_plan import TravelPlan
from ...schemas.base import ApiResponse
from ...schemas.recommendations import (
    AccommodationOptionSchema,
    AccommodationRecommendationsResponse,
    FlightOptionSchema,
    FlightRecommendationsResponse,
)
from ...services.recommendations import AccommodationRecommender, FlightRecommender


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


async def _get_plan_or_404(
    plan_id: UUID,
    user_id: str,
    session: AsyncSession,
) -> TravelPlan:
    try:
        user_uuid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        ) from exc

    result = await session.execute(
        select(TravelPlan).where(TravelPlan.id == plan_id, TravelPlan.user_id == user_uuid)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel plan not found",
        )
    return plan


@router.get(
    "/flights/{plan_id}",
    response_model=ApiResponse[FlightRecommendationsResponse],
)
async def get_flight_recommendations(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[FlightRecommendationsResponse]:
    """Return flight recommendations for a travel plan"""
    plan = await _get_plan_or_404(plan_id, user_id, session)
    service = FlightRecommender(session)
    result = await service.get_recommendations(plan)
    payload = FlightRecommendationsResponse(
        plan_id=plan.id,
        origin_airport=result.origin_airport,
        destination_airport=result.destination_airport,
        options=[FlightOptionSchema.model_validate(option) for option in result.options],
    )
    return ApiResponse(success=True, data=payload)


@router.get(
    "/accommodations/{plan_id}",
    response_model=ApiResponse[AccommodationRecommendationsResponse],
)
async def get_accommodation_recommendations(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[AccommodationRecommendationsResponse]:
    """Return accommodation recommendations for a travel plan"""
    plan = await _get_plan_or_404(plan_id, user_id, session)
    service = AccommodationRecommender(session)
    result = await service.get_recommendations(plan)
    payload = AccommodationRecommendationsResponse(
        plan_id=plan.id,
        check_in=result.check_in,
        check_out=result.check_out,
        options=[
            AccommodationOptionSchema.model_validate(option) for option in result.options
        ],
    )
    return ApiResponse(success=True, data=payload)
