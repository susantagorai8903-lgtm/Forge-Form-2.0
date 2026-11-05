from datetime import datetime, time
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_correlation_id, require_roles
from app.database.session import get_db
from app.models import Booking, BookingStatusHistory, Program, Trainer, User
from app.schemas import BookingCreate, BookingStatusUpdate
from app.services.outbox import add_outbox_event, queue_notification

router = APIRouter()
admin_router = APIRouter(prefix="/admin/bookings")
admin = require_roles("ADMIN", "SUPER_ADMIN", "STAFF")
VALID_TRANSITIONS = {
    "PENDING": {"CONFIRMED", "CANCELLED", "REJECTED"},
    "CONFIRMED": {"CANCELLED", "COMPLETED"},
    "CANCELLED": set(),
    "COMPLETED": set(),
    "REJECTED": set(),
}


def parse_preferred_time(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError:
        return datetime.strptime(value, "%I:%M %p").time()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: BookingCreate,
    db: AsyncSession = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    correlation_id: str = Depends(get_correlation_id),
):
    if request.website:
        raise HTTPException(status_code=400, detail="Invalid submission")
    if idempotency_key:
        if len(idempotency_key) > 128:
            raise HTTPException(status_code=422, detail="Idempotency key is too long")
        previous = await db.scalar(select(Booking).where(Booking.idempotency_key == idempotency_key))
        if previous is not None:
            return {"id": str(previous.id), "message": "Your consultation request has already been received."}

    try:
        timezone_name = request.timezone or settings.booking_timezone
        timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail="Invalid timezone") from exc
    if request.date < datetime.now(timezone).date():
        raise HTTPException(status_code=422, detail="Preferred date cannot be in the past")

    program = await db.scalar(select(Program).where(Program.is_active.is_(True), (Program.slug == request.program) | (Program.name == request.program)))
    if program is None:
        raise HTTPException(status_code=422, detail="Selected program is not available")
    preferred_time = parse_preferred_time(request.time)
    if settings.booking_capacity_per_slot > 0:
        booked = await db.scalar(select(func.count()).select_from(Booking).where(
            Booking.preferred_date == request.date,
            Booking.preferred_time == preferred_time,
            Booking.booking_status == "CONFIRMED",
        ))
        if (booked or 0) >= settings.booking_capacity_per_slot:
            raise HTTPException(status_code=409, detail="This requested time is no longer available")

    booking = Booking(
        idempotency_key=idempotency_key,
        customer_name=request.name,
        email=request.email.lower(),
        phone=request.phone,
        program_id=program.id,
        preferred_date=request.date,
        preferred_time=preferred_time,
        timezone=timezone_name,
        fitness_goals=request.goals,
        additional_notes=request.notes,
        booking_status="PENDING",
    )
    try:
        db.add(booking)
        await db.flush()
        db.add(BookingStatusHistory(booking_id=booking.id, old_status=None, new_status="PENDING"))
        db.add(add_outbox_event(
            "booking",
            booking.id,
            "forgeform.booking.created",
            {"booking_id": str(booking.id), "program": program.name},
            correlation_id,
        ))
        booking_details = (
            f"Name: {booking.customer_name}\nEmail: {booking.email}\nPhone: {booking.phone}\n"
            f"Program: {program.name}\nPreferred date: {booking.preferred_date.isoformat()}\n"
            f"Preferred time: {booking.preferred_time.strftime('%I:%M %p').lstrip('0')} ({booking.timezone})\n"
            f"Goals: {booking.fitness_goals}\nNotes: {booking.additional_notes or 'None'}"
        )
        await queue_notification(
            db, booking.id, booking.email, "booking.received",
            "We received your consultation request",
            f"Your consultation request has been received and is pending studio confirmation.\n\n{booking_details}",
            correlation_id,
        )
        await queue_notification(
            db, booking.id, settings.business_email, "booking.internal",
            "New Forge & Form consultation request",
            booking_details,
            correlation_id,
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if idempotency_key:
            previous = await db.scalar(select(Booking).where(Booking.idempotency_key == idempotency_key))
            if previous is not None:
                return {"id": str(previous.id), "message": "Your consultation request has already been received."}
        raise HTTPException(status_code=409, detail="Booking could not be saved due to a conflicting request") from exc
    return {"id": str(booking.id), "message": "Your consultation request has been received. The studio will follow up to confirm the details."}


@router.get("/availability")
async def availability(
    date_value: str = Query(alias="date"),
    time_value: str | None = Query(default=None, alias="time"),
    db: AsyncSession = Depends(get_db),
):
    try:
        chosen_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        if chosen_date < datetime.now(ZoneInfo(settings.booking_timezone)).date():
            return {"available": False}
        if time_value:
            parse_preferred_time(time_value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid date or time") from exc
    available = True
    if time_value and settings.booking_capacity_per_slot > 0:
        count = await db.scalar(select(func.count()).select_from(Booking).where(
            Booking.preferred_date == chosen_date,
            Booking.preferred_time == parse_preferred_time(time_value),
            Booking.booking_status == "CONFIRMED",
        ))
        available = (count or 0) < settings.booking_capacity_per_slot
    return {"date": chosen_date.isoformat(), "time": time_value, "available": available}


@router.get("/{booking_id}")
async def get_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"id": str(booking.id), "status": booking.booking_status, "date": booking.preferred_date.isoformat(),
            "time": booking.preferred_time.strftime("%I:%M %p").lstrip("0"), "program": booking.program.name}


@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if "CANCELLED" not in VALID_TRANSITIONS.get(booking.booking_status, set()):
        raise HTTPException(status_code=409, detail="Booking cannot be cancelled in its current state")
    old_status = booking.booking_status
    booking.booking_status = "CANCELLED"
    db.add(BookingStatusHistory(booking_id=booking.id, old_status=old_status, new_status="CANCELLED"))
    db.add(add_outbox_event("booking", booking.id, "forgeform.booking.cancelled", {"booking_id": str(booking.id)}))
    await queue_notification(
        db, booking.id, booking.email, "booking.cancelled",
        "Your consultation request was cancelled",
        f"Your Forge & Form consultation request ({booking.id}) was cancelled. Contact {settings.business_email} if you need help.",
    )
    await db.commit()
    return {"id": str(booking.id), "status": booking.booking_status}


@admin_router.get("")
async def list_bookings(
    _user: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = (await db.scalars(select(Booking).order_by(Booking.created_at.desc()).limit(limit).offset(offset))).all()
    return [{"id": str(row.id), "name": row.customer_name, "email": row.email, "phone": row.phone,
             "program": row.program.name, "date": row.preferred_date.isoformat(), "time": row.preferred_time.isoformat(),
             "status": row.booking_status, "goals": row.fitness_goals} for row in rows]


@admin_router.patch("/{booking_id}/status")
async def set_booking_status(booking_id: UUID, request: BookingStatusUpdate, user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if request.status == booking.booking_status:
        return {"id": str(booking.id), "status": booking.booking_status}
    if request.status not in VALID_TRANSITIONS.get(booking.booking_status, set()):
        raise HTTPException(status_code=409, detail="Invalid booking status transition")
    if request.status == "CONFIRMED" and settings.booking_capacity_per_slot > 0:
        await db.scalar(select(Program).where(Program.id == booking.program_id).with_for_update())
        confirmed = await db.scalar(select(func.count()).select_from(Booking).where(
            Booking.preferred_date == booking.preferred_date,
            Booking.preferred_time == booking.preferred_time,
            Booking.booking_status == "CONFIRMED",
            Booking.id != booking.id,
        ))
        if (confirmed or 0) >= settings.booking_capacity_per_slot:
            raise HTTPException(status_code=409, detail="This requested time is at capacity")
    old_status = booking.booking_status
    booking.booking_status = request.status
    db.add(BookingStatusHistory(booking_id=booking.id, old_status=old_status, new_status=request.status, changed_by_id=user.id))
    event_type = "forgeform.booking.confirmed" if request.status == "CONFIRMED" else (
        "forgeform.booking.cancelled" if request.status == "CANCELLED" else "forgeform.booking.updated"
    )
    db.add(add_outbox_event("booking", booking.id, event_type, {"booking_id": str(booking.id), "status": request.status}))
    await queue_notification(
        db, booking.id, booking.email, f"booking.{request.status.lower()}",
        f"Your consultation request status is {request.status.lower()}",
        f"Your Forge & Form consultation request status has been updated to {request.status.lower()}.",
    )
    await db.commit()
    return {"id": str(booking.id), "status": booking.booking_status}


@admin_router.patch("/{booking_id}/assign-trainer")
async def assign_trainer(booking_id: UUID, body: dict[str, str], _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    try:
        trainer_id = UUID(body.get("trainer_id", ""))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="A valid trainer_id is required") from exc
    trainer = await db.get(Trainer, trainer_id)
    if booking is None or trainer is None or not trainer.is_active:
        raise HTTPException(status_code=404, detail="Booking or active trainer not found")
    booking.assigned_trainer_id = trainer.id
    await db.commit()
    return {"id": str(booking.id), "assigned_trainer_id": str(trainer.id)}
