import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator

SkinType = Literal["normal", "oily", "dry", "combination", "sensitive"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None
    skin_type: SkinType | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut
