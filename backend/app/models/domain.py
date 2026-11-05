import uuid
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import (
    JSON, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer,
    String, Table, Text, Time, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid as UUID

from app.database.base import Base


def new_id() -> uuid.UUID:
    return uuid.uuid4()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(secondary=user_roles, back_populates="roles")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    roles: Mapped[list[Role]] = relationship(secondary=user_roles, back_populates="users", lazy="selectin")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("refresh_tokens.id"))
    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class ProgramCategory(Base):
    __tablename__ = "program_categories"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    programs: Mapped[list["Program"]] = relationship(back_populates="category")


class Program(TimestampMixin, Base):
    __tablename__ = "programs"
    __table_args__ = (CheckConstraint("display_order >= 0", name="ck_program_display_order_nonnegative"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("program_categories.id", ondelete="RESTRICT"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    short_description: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    benefits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[ProgramCategory] = relationship(back_populates="programs", lazy="joined")


class Trainer(TimestampMixin, Base):
    __tablename__ = "trainers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    designation: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    biography: Mapped[str] = mapped_column(Text, nullable=False, default="")
    profile_image: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    specializations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    experience_years: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (CheckConstraint("experience_years IS NULL OR experience_years >= 0", name="ck_trainer_experience_nonnegative"),)


class Booking(TimestampMixin, Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("booking_status IN ('PENDING','CONFIRMED','CANCELLED','COMPLETED','REJECTED')", name="ck_booking_status"),
        Index("ix_booking_slot_status", "preferred_date", "preferred_time", "booking_status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False)
    preferred_date: Mapped[date] = mapped_column(Date, nullable=False)
    preferred_time: Mapped[time] = mapped_column(Time, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    fitness_goals: Mapped[str] = mapped_column(Text, nullable=False)
    additional_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    booking_status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    assigned_trainer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("trainers.id", ondelete="SET NULL"))
    program: Mapped[Program] = relationship(lazy="joined")
    assigned_trainer: Mapped[Trainer | None] = relationship()
    history: Mapped[list["BookingStatusHistory"]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class BookingStatusHistory(Base):
    __tablename__ = "booking_status_history"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(16))
    new_status: Mapped[str] = mapped_column(String(16), nullable=False)
    changed_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    booking: Mapped[Booking] = relationship(back_populates="history")


class ContactEnquiry(TimestampMixin, Base):
    __tablename__ = "contact_enquiries"
    __table_args__ = (CheckConstraint("enquiry_status IN ('NEW','CONTACTED','QUALIFIED','CONVERTED','CLOSED')", name="ck_enquiry_status"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    interested_program: Mapped[str] = mapped_column(String(120), nullable=False)
    fitness_goals: Mapped[str] = mapped_column(String(240), nullable=False)
    preferred_contact_method: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String(2000), nullable=False)
    enquiry_status: Mapped[str] = mapped_column(String(16), nullable=False, default="NEW")
    source: Mapped[str] = mapped_column(String(120), nullable=False, default="website")


class Testimonial(TimestampMixin, Base):
    __tablename__ = "testimonials"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_testimonial_rating"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_image: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    program_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("programs.id", ondelete="SET NULL"))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BlogCategory(Base):
    __tablename__ = "blog_categories"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="category")


class BlogPost(TimestampMixin, Base):
    __tablename__ = "blog_posts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    excerpt: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    featured_image: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    author_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    author_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Forge & Form Editorial")
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("blog_categories.id", ondelete="RESTRICT"), nullable=False)
    reading_time: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    category: Mapped[BlogCategory] = relationship(back_populates="posts", lazy="joined")


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(60), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False, default="USA")
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    opening_hours: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    recipient: Mapped[str] = mapped_column(String(254), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EventOutbox(Base):
    __tablename__ = "event_outbox"
    __table_args__ = (Index("ix_outbox_pending", "status", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, default=new_id)
    aggregate_type: Mapped[str] = mapped_column(String(80), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MarketingEvent(Base):
    __tablename__ = "marketing_events"
    __table_args__ = (Index("ix_marketing_event_time", "event_type", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_id)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False, default="website")
    campaign: Mapped[str | None] = mapped_column(String(160))
    landing_page: Mapped[str | None] = mapped_column(String(500))
    anonymous_session_id: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProcessedEvent(Base):
    __tablename__ = "processed_events"
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    handler: Mapped[str] = mapped_column(String(100), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
