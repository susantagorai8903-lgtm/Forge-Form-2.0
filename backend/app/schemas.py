import json
import re
from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    program: str = Field(min_length=1, max_length=120)
    goals: str = Field(min_length=1, max_length=240)
    preferredContact: str = Field(alias="preferredContact", min_length=1, max_length=16)
    message: str = Field(min_length=1, max_length=2000)
    website: str = Field(default="", max_length=0)

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        if not re.fullmatch(r"[+()\d.\-\s]{7,30}", value) or sum(char.isdigit() for char in value) < 7:
            raise ValueError("Enter a valid phone number")
        return value

    @field_validator("preferredContact")
    @classmethod
    def valid_contact_method(cls, value: str) -> str:
        if value.lower() not in {"email", "phone"}:
            raise ValueError("Choose email or phone")
        return value.lower()


class BookingCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    program: str = Field(min_length=1, max_length=120)
    date: date
    time: str = Field(min_length=1, max_length=40)
    goals: str = Field(min_length=1, max_length=1200)
    notes: str = Field(default="", max_length=1200)
    timezone: str | None = Field(default=None, max_length=64)
    website: str = Field(default="", max_length=0)

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        if not re.fullmatch(r"[+()\d.\-\s]{7,30}", value) or sum(char.isdigit() for char in value) < 7:
            raise ValueError("Enter a valid phone number")
        return value

    @field_validator("time")
    @classmethod
    def valid_time(cls, value: str) -> str:
        try:
            time.fromisoformat(value)
        except ValueError:
            try:
                datetime.strptime(value, "%I:%M %p")
            except ValueError as exc:
                raise ValueError("Use a time such as 9:00 AM") from exc
        return value


class BookingStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        value = value.upper()
        if value not in {"PENDING", "CONFIRMED", "CANCELLED", "COMPLETED", "REJECTED"}:
            raise ValueError("Unsupported booking status")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProgramWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    category: str = Field(min_length=1, max_length=80)
    description: str = ""
    short_description: str = Field(default="", max_length=300)
    benefits: list[str] = Field(default_factory=list)
    target_audience: str = ""
    image_url: str = Field(default="", max_length=500)
    is_active: bool = True
    display_order: int = Field(default=0, ge=0)


class ContactStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        value = value.upper()
        if value not in {"NEW", "CONTACTED", "QUALIFIED", "CONVERTED", "CLOSED"}:
            raise ValueError("Unsupported enquiry status")
        return value


class TrainerWrite(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    designation: str = Field(default="", max_length=120)
    biography: str = ""
    profile_image: str = Field(default="", max_length=500)
    specializations: list[str] = Field(default_factory=list)
    experience_years: int | None = Field(default=None, ge=0)
    is_active: bool = True


class TestimonialWrite(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_image: str = Field(default="", max_length=500)
    content: str = Field(min_length=1, max_length=4000)
    rating: int = Field(ge=1, le=5)
    program_id: UUID | None = None
    is_published: bool = False


class BlogWrite(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=220)
    excerpt: str = Field(min_length=1, max_length=500)
    content: list[str] = Field(min_length=1)
    featured_image: str = Field(default="", max_length=500)
    category_id: UUID
    reading_time: str = Field(default="", max_length=40)
    is_published: bool = False
    published_at: datetime | None = None


class LocationWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    address: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=60)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(default="USA", max_length=80)
    phone: str = Field(min_length=7, max_length=30)
    email: EmailStr
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    opening_hours: dict[str, Any] | None = None
    is_active: bool = True


class AdminUserView(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    roles: list[str]


class AnalyticsOverview(BaseModel):
    enquiries: int
    bookings: int
    pending_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    enquiry_to_booking_rate: float
    booking_confirmation_rate: float


class MarketingEventCreate(BaseModel):
    event_type: str = Field(pattern="^(PAGE_VIEW|PROGRAM_VIEW|CTA_CLICK|CONTACT_SUBMITTED|BOOKING_STARTED|BOOKING_SUBMITTED|BOOKING_CONFIRMED)$")
    source: str = Field(default="website", max_length=120)
    campaign: str | None = Field(default=None, max_length=160)
    landing_page: str | None = Field(default=None, max_length=500)
    anonymous_session_id: str | None = Field(default=None, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def limit_metadata_size(cls, value: dict[str, Any]) -> dict[str, Any]:
        try:
            size = len(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        except (TypeError, ValueError) as exc:
            raise ValueError("Metadata must contain JSON-serializable values") from exc
        if size > 8192:
            raise ValueError("Metadata must be 8 KiB or smaller")
        return value
