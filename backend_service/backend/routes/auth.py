from fastapi import APIRouter

from backend.core.auth import get_current_user
from backend.models.auth import AuthResponse, CurrentUserResponse, LoginRequest, RegisterRequest
from backend.services.auth_service import authenticate_user, register_user
from fastapi import Depends


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest):
    return register_user(data.name, data.username, data.email, data.password)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    return authenticate_user(data.email, data.password)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: dict = Depends(get_current_user)):
    return current_user
