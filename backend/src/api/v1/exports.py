"""Exports API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_db
from ...core.security import get_current_user_id
from ...schemas.base import ApiResponse
from ...schemas.exports import MapExportResponse
from ...schemas.pdf import PdfExportResponse
from ...services.exports import MapExportError, MapExportNotFoundError, MapExportService
from ...services.pdf.generator import (
    PdfGenerationError,
    PdfGeneratorService,
    PdfPlanNotFoundError,
)


router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/map/{plan_id}", response_model=ApiResponse[MapExportResponse])
async def get_map_export(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[MapExportResponse]:
    """Return map visualization payload for a travel plan."""
    service = MapExportService(session)
    try:
        payload = await service.build_map_export(plan_id, UUID(user_id))
    except MapExportNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Travel plan not found")
    except MapExportError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return ApiResponse(success=True, data=payload)


@router.get("/pdf/{plan_id}", response_model=ApiResponse[PdfExportResponse])
async def get_pdf_export(
    plan_id: UUID,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[PdfExportResponse]:
    """Generate and return a signed download URL for the itinerary PDF."""
    service = PdfGeneratorService(session)
    try:
        result = await service.generate(plan_id, UUID(user_id))
    except PdfPlanNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Travel plan not found")
    except PdfGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    response = PdfExportResponse(
        file_name=result.file_name,
        download_url=result.download_url,
        storage_path=result.storage_path,
        expires_at=result.expires_at,
    )
    return ApiResponse(success=True, data=response)
