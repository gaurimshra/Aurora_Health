from fastapi import APIRouter, Depends

from backend.core.auth import get_current_user
from backend.models.health import ProgressCoachRequest, ProgressCoachResponse, ProgressLogRequest
from backend.services.progress_service import get_progress_summary, log_progress, progress_coach


router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/log")
def create_progress_log(data: ProgressLogRequest, current_user: dict = Depends(get_current_user)):
    return log_progress(current_user["user_id"], data.model_dump(exclude={"user_id"}))


@router.get("/me")
def fetch_progress(current_user: dict = Depends(get_current_user)):
    return get_progress_summary(current_user["user_id"])


@router.post("/coach", response_model=ProgressCoachResponse)
def coach(data: ProgressCoachRequest, current_user: dict = Depends(get_current_user)):
    return progress_coach(current_user["user_id"], data.message)
