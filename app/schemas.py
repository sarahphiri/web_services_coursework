from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"