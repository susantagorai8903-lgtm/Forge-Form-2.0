from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import Booking, ContactEnquiry, MarketingEvent, Program, User
from app.schemas import AnalyticsOverview, MarketingEventCreate
from app.services.outbox import add_outbox_event

router = APIRouter()
analytics_router = APIRouter(prefix="/admin/analytics")
admin = require_roles("ADMIN", "SUPER_ADMIN", "STAFF")


@router.post("", status_code=202)
async def record_marketing_event(request: MarketingEventCreate, db: AsyncSession = Depends(get_db)):
    row = MarketingEvent(
        event_type=request.event_type,
        source=request.source,
        campaign=request.campaign,
        landing_page=request.landing_page,
        anonymous_session_id=request.anonymous_session_id,
        metadata_json=request.metadata,
    )
    db.add(row)
    await db.flush()
    db.add(add_outbox_event("marketing_event", row.id, "forgeform.analytics.event", {
        "event_id": str(row.id), "event_type": row.event_type, "source": row.source,
        "campaign": row.campaign, "landing_page": row.landing_page,
    }))
    await db.commit()
    return {"id": str(row.id)}


@analytics_router.get("/overview", response_model=AnalyticsOverview)
async def analytics_overview(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    enquiries = await db.scalar(select(func.count()).select_from(ContactEnquiry)) or 0
    bookings = await db.scalar(select(func.count()).select_from(Booking)) or 0
    pending = await db.scalar(select(func.count()).select_from(Booking).where(Booking.booking_status == "PENDING")) or 0
    confirmed = await db.scalar(select(func.count()).select_from(Booking).where(Booking.booking_status == "CONFIRMED")) or 0
    cancelled = await db.scalar(select(func.count()).select_from(Booking).where(Booking.booking_status == "CANCELLED")) or 0
    return {
        "enquiries": enquiries,
        "bookings": bookings,
        "pending_bookings": pending,
        "confirmed_bookings": confirmed,
        "cancelled_bookings": cancelled,
        "enquiry_to_booking_rate": round(bookings / enquiries, 4) if enquiries else 0.0,
        "booking_confirmation_rate": round(confirmed / bookings, 4) if bookings else 0.0,
    }


@analytics_router.get("/bookings")
async def booking_analytics(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    status_rows = (await db.execute(select(Booking.booking_status, func.count()).group_by(Booking.booking_status))).all()
    program_rows = (await db.execute(
        select(Program.name, func.count(Booking.id)).join(Booking, Booking.program_id == Program.id, isouter=True).group_by(Program.name)
    )).all()
    return {
        "by_status": {status: count for status, count in status_rows},
        "program_interest": [{"program": name, "bookings": count} for name, count in program_rows],
    }


@analytics_router.get("/enquiries")
async def enquiry_analytics(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    status_rows = (await db.execute(select(ContactEnquiry.enquiry_status, func.count()).group_by(ContactEnquiry.enquiry_status))).all()
    source_rows = (await db.execute(select(ContactEnquiry.source, func.count()).group_by(ContactEnquiry.source))).all()
    return {
        "by_status": {status: count for status, count in status_rows},
        "lead_sources": [{"source": source, "enquiries": count} for source, count in source_rows],
    }


@analytics_router.get("/conversion")
async def conversion_analytics(
    _user: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
    campaign: str | None = Query(default=None, max_length=160),
):
    query = select(MarketingEvent.source, MarketingEvent.campaign, MarketingEvent.event_type, func.count()).group_by(
        MarketingEvent.source, MarketingEvent.campaign, MarketingEvent.event_type
    )
    if campaign:
        query = query.where(MarketingEvent.campaign == campaign)
    rows = (await db.execute(query)).all()
    return {
        "denominators": {
            "enquiry_to_booking_rate": "all bookings / all contact enquiries",
            "booking_confirmation_rate": "confirmed bookings / all bookings",
        },
        "campaign_performance": [
            {"source": source, "campaign": name, "event_type": event_type, "count": count}
            for source, name, event_type, count in rows
        ],
    }
