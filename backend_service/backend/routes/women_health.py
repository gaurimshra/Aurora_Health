from fastapi import APIRouter, Depends, HTTPException

from backend.core.auth import get_current_user
from backend.models.health import CyclePredictionResponse, PeriodLogRequest
from backend.services.women_health_service import get_women_health_dashboard, log_period_entry


router = APIRouter(prefix="/women-health", tags=["women-health"])


@router.post("/log-period")
def log_period(data: PeriodLogRequest, current_user: dict = Depends(get_current_user)):
    try:
        return log_period_entry(current_user["user_id"], data.model_dump(exclude={"user_id"}))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/dashboard", response_model=CyclePredictionResponse)
def women_health_dashboard(current_user: dict = Depends(get_current_user)):
    return get_women_health_dashboard(current_user["user_id"])
