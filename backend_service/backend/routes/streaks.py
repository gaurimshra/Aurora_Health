from fastapi import APIRouter, Depends

from backend.core.auth import get_current_user
from backend.models.health import StreakCheckInRequest, StreakResponse
from backend.services.streak_service import get_streak, record_checkin


router = APIRouter(prefix="/streaks", tags=["streaks"])


@router.post("/check-in", response_model=StreakResponse)
def check_in(data: StreakCheckInRequest, current_user: dict = Depends(get_current_user)):
    return record_checkin(current_user["user_id"], data.model_dump(exclude={"user_id"}))


@router.get("/me", response_model=StreakResponse)
def fetch_streak(current_user: dict = Depends(get_current_user)):
    return get_streak(current_user["user_id"])
