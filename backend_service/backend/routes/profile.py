from fastapi import APIRouter, Depends, HTTPException

from backend.core.auth import get_current_user
from backend.models.health import UserProfileRequest, UserProfileResponse
from backend.services.profile_service import get_user_profile, save_user_profile


router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("", response_model=UserProfileResponse)
def save_profile(data: UserProfileRequest, current_user: dict = Depends(get_current_user)):
    return save_user_profile(current_user["user_id"], data.model_dump(exclude={"user_id"}))


@router.get("/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    profile = get_user_profile(current_user["user_id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile
