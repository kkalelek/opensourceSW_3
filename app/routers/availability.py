from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.availability import (
    AvailableNowResponse,
    AvailableRangeResponse,
    ParsedScheduleSummary,
)
from app.services.timetable_service import get_timetable_service

router = APIRouter(tags=["availability"])


@router.get("/api/availability/summary", response_model=ParsedScheduleSummary)
def get_schedule_summary() -> ParsedScheduleSummary:
    service = get_timetable_service()
    return service.get_summary()


@router.get(
    "/api/buildings/{building}/available-now",
    response_model=AvailableNowResponse,
)
def get_available_now(building: str) -> AvailableNowResponse:
    service = get_timetable_service()

    try:
        return service.get_available_now(building)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/api/buildings/{building}/available-range",
    response_model=AvailableRangeResponse,
)
def get_available_range(
    building: str,
    day: str = Query(..., description="Weekday code such as MON"),
    start: str = Query(..., description="Start time in HH:MM format"),
    end: str = Query(..., description="End time in HH:MM format"),
) -> AvailableRangeResponse:
    service = get_timetable_service()

    try:
        return service.get_available_range(building=building, day=day, start=start, end=end)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
