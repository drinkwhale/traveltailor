"""Travel plan API endpoints"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_db
from ...core.security import get_current_user_id
from ...models.travel_plan import TravelPlan
from ...schemas.base import ApiResponse, PaginatedResponse
from ...schemas.travel_plan import (
    TravelPlanCreate,
    TravelPlanResponse,
    TravelPlanStatusResponse,
    TravelPlanSummary,
    TravelPlanUpdate,
)
from ...services.ai.planner import TravelPlanner


router = APIRouter(prefix="/travel-plans", tags=["Travel Plans"])


async def _get_plan_or_404(
    plan_id: UUID,
    user_id: str,
    session: AsyncSession,
) -> TravelPlan:
    user_uuid = UUID(user_id)
    result = await session.execute(
        select(TravelPlan).where(TravelPlan.id == plan_id, TravelPlan.user_id == user_uuid)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Travel plan not found")
    return plan


@router.post("", response_model=ApiResponse[TravelPlanResponse], status_code=status.HTTP_201_CREATED)
async def create_travel_plan(
    payload: TravelPlanCreate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[TravelPlanResponse]:
    planner = TravelPlanner(session)
    plan = await planner.generate_plan(UUID(user_id), payload)
    response = await planner.build_response(plan)
    return ApiResponse(success=True, data=response)


@router.get("/{plan_id}", response_model=ApiResponse[TravelPlanResponse])
async def get_travel_plan(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[TravelPlanResponse]:
    plan = await _get_plan_or_404(plan_id, user_id, session)
    planner = TravelPlanner(session)
    response = await planner.build_response(plan)
    return ApiResponse(success=True, data=response)


@router.get("/{plan_id}/status", response_model=ApiResponse[TravelPlanStatusResponse])
async def get_travel_plan_status(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[TravelPlanStatusResponse]:
    plan = await _get_plan_or_404(plan_id, user_id, session)
    status_payload = TravelPlanStatusResponse(
        id=plan.id,
        status=plan.status,  # type: ignore[arg-type]
        progress=1.0 if plan.status == "completed" else 0.5,
        message="Plan ready" if plan.status == "completed" else "Plan generation in progress",
    )
    return ApiResponse(success=True, data=status_payload)


@router.get("", response_model=ApiResponse[PaginatedResponse[TravelPlanSummary]])
async def list_travel_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[PaginatedResponse[TravelPlanSummary]]:
    offset = (page - 1) * page_size
    user_uuid = UUID(user_id)

    total_result = await session.execute(
        select(func.count()).select_from(TravelPlan).where(TravelPlan.user_id == user_uuid)
    )
    total = total_result.scalar() or 0

    result = await session.execute(
        select(TravelPlan)
        .where(TravelPlan.user_id == user_uuid)
        .order_by(TravelPlan.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    plans = result.scalars().all()
    summaries = [TravelPlanSummary.model_validate(plan) for plan in plans]

    paginated = PaginatedResponse.create(
        items=summaries,
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(success=True, data=paginated)


@router.patch("/{plan_id}", response_model=ApiResponse[TravelPlanResponse])
async def update_travel_plan(
    plan_id: UUID,
    payload: TravelPlanUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[TravelPlanResponse]:
    plan = await _get_plan_or_404(plan_id, user_id, session)

    update_data: dict[str, Any] = {}
    if payload.title is not None:
        update_data["title"] = payload.title
    if payload.status is not None:
        update_data["status"] = payload.status
    if payload.preferences is not None:
        update_data["preferences"] = payload.preferences

    if update_data:
        await session.execute(
            update(TravelPlan)
            .where(TravelPlan.id == plan.id)
            .values(**update_data)
        )
        await session.commit()
        await session.refresh(plan)

    planner = TravelPlanner(session)
    response = await planner.build_response(plan)
    return ApiResponse(success=True, data=response)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_travel_plan(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> None:
    await _get_plan_or_404(plan_id, user_id, session)
    user_uuid = UUID(user_id)
    await session.execute(
        delete(TravelPlan).where(TravelPlan.id == plan_id, TravelPlan.user_id == user_uuid)
    )
    await session.commit()
