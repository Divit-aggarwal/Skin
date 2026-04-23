import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

SkinType = Literal["normal", "oily", "dry", "combination", "sensitive"]


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    display_name: str | None
    age: int | None
    gender: str | None
    skin_type: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    age: int | None = Field(default=None, ge=1, le=120)
    gender: str | None = None
    skin_type: SkinType | None = None


class DeleteAccountRequest(BaseModel):
    password: str
