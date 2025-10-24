from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .models import BookingStatus


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class SessionOut(BaseModel):
    id: int
    user_id: int
    expires_at: datetime

    class Config:
        from_attributes = True


class PodBase(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: int
    price_cents: int
    is_active: bool = True


class PodCreate(PodBase):
    pass


class PodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    price_cents: Optional[int] = None
    is_active: Optional[bool] = None


class PodOut(PodBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    user_id: int
    pod_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.confirmed
    total_price_cents: int


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    total_price_cents: Optional[int] = None


class BookingOut(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


