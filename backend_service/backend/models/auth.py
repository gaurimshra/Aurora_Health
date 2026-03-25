from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str
    username: str


class CurrentUserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    username: str
