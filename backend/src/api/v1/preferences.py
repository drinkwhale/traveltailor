"""User preference API endpoints"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_db
from ...core.security import get_current_user_id
from ...models.user_preference import UserPreference
from ...schemas.base import ApiResponse
from ...schemas.preferences import UserPreferenceResponse, UserPreferenceUpdate
from ...services.preferences.learning import PreferenceLearningService

router = APIRouter(prefix="/preferences", tags=["Preferences"])


async def _get_user_preference(session: AsyncSession, user_id: UUID) -> UserPreference | None:
    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    return result.scalar_one_or_none()


def _to_iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if isinstance(dt, datetime) else None


def _merge(primary: list[str] | None, fallback: list[str]) -> list[str]:
    merged: list[str] = []
    for value in primary or []:
        if value and value not in merged:
            merged.append(value)
    for value in fallback:
        if value and value not in merged:
            merged.append(value)
    return merged


def _build_response(
    preference: UserPreference | None,
    summary_data: dict[str, object],
) -> UserPreferenceResponse:
    default_budget_min = preference.default_budget_min if preference else None
    default_budget_max = preference.default_budget_max if preference else None

    response = UserPreferenceResponse(
        default_budget_min=default_budget_min
        if default_budget_min is not None
        else summary_data.get("default_budget_min"),
        default_budget_max=default_budget_max
        if default_budget_max is not None
        else summary_data.get("default_budget_max"),
        preferred_traveler_types=_merge(
            preference.preferred_traveler_types if preference else None,
            summary_data.get("preferred_traveler_types", []) or [],
        ),
        preferred_interests=_merge(
            preference.preferred_interests if preference else None,
            summary_data.get("preferred_interests", []) or [],
        ),
        avoided_activities=_merge(
            preference.avoided_activities if preference else None,
            summary_data.get("avoided_activities", []) or [],
        ),
        dietary_restrictions=_merge(
            preference.dietary_restrictions if preference else None,
            summary_data.get("dietary_restrictions", []) or [],
        ),
        preferred_accommodation_type=_merge(
            preference.preferred_accommodation_type if preference else None,
            summary_data.get("preferred_accommodation_type", []) or [],
        ),
        mobility_considerations=preference.mobility_considerations if preference else None,
        preferred_pace=summary_data.get("preferred_pace"),
        recent_notes=summary_data.get("recent_notes"),
        last_budget_total=summary_data.get("last_budget_total"),
        updated_at=_to_iso(getattr(preference, "updated_at", None)),
    )
    return response


@router.get("", response_model=ApiResponse[UserPreferenceResponse])
async def get_preferences(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[UserPreferenceResponse]:
    user_uuid = UUID(user_id)
    preference = await _get_user_preference(session, user_uuid)

    learning = PreferenceLearningService(session)
    summary = await learning.summarize_user_preferences(user_uuid)
    summary_dict = {
        "default_budget_min": summary.default_budget_min,
        "default_budget_max": summary.default_budget_max,
        "preferred_traveler_types": summary.preferred_traveler_types,
        "preferred_interests": summary.preferred_interests,
        "avoided_activities": summary.avoided_activities,
        "dietary_restrictions": summary.dietary_restrictions,
        "preferred_accommodation_type": summary.preferred_accommodation_type,
        "preferred_pace": summary.preferred_pace,
        "recent_notes": summary.recent_notes,
        "last_budget_total": summary.last_budget_total,
    }

    response = _build_response(preference, summary_dict)
    return ApiResponse(success=True, data=response)


@router.put("", response_model=ApiResponse[UserPreferenceResponse], status_code=status.HTTP_200_OK)
async def update_preferences(
    payload: UserPreferenceUpdate,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[UserPreferenceResponse]:
    user_uuid = UUID(user_id)
    preference = await _get_user_preference(session, user_uuid)
    if not preference:
        preference = UserPreference(user_id=user_uuid)
        session.add(preference)

    preference.default_budget_min = payload.default_budget_min
    preference.default_budget_max = payload.default_budget_max
    preference.preferred_traveler_types = payload.preferred_traveler_types
    preference.preferred_interests = payload.preferred_interests
    preference.avoided_activities = payload.avoided_activities
    preference.dietary_restrictions = payload.dietary_restrictions
    preference.preferred_accommodation_type = payload.preferred_accommodation_type
    preference.mobility_considerations = payload.mobility_considerations

    await session.commit()
    await session.refresh(preference)

    learning = PreferenceLearningService(session)
    summary = await learning.summarize_user_preferences(user_uuid)
    summary_dict = {
        "default_budget_min": summary.default_budget_min,
        "default_budget_max": summary.default_budget_max,
        "preferred_traveler_types": summary.preferred_traveler_types,
        "preferred_interests": summary.preferred_interests,
        "avoided_activities": summary.avoided_activities,
        "dietary_restrictions": summary.dietary_restrictions,
        "preferred_accommodation_type": summary.preferred_accommodation_type,
        "preferred_pace": summary.preferred_pace,
        "recent_notes": summary.recent_notes,
        "last_budget_total": summary.last_budget_total,
    }

    response = _build_response(preference, summary_dict)
    return ApiResponse(success=True, data=response)
