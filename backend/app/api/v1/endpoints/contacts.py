from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_correlation_id, require_roles
from app.database.session import get_db
from app.models import ContactEnquiry, User
from app.schemas import ContactCreate, ContactStatusUpdate
from app.core.config import settings
from app.services.outbox import add_outbox_event, queue_notification

router = APIRouter()
admin = require_roles("ADMIN", "SUPER_ADMIN", "STAFF")


@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: ContactCreate,
    db: AsyncSession = Depends(get_db),
    correlation_id: str = Depends(get_correlation_id),
):
    if request.website:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid submission")
    enquiry = ContactEnquiry(
        full_name=request.name,
        email=request.email.lower(),
        phone=request.phone,
        interested_program=request.program,
        fitness_goals=request.goals,
        preferred_contact_method=request.preferredContact,
        message=request.message,
        source="website",
    )
    db.add(enquiry)
    await db.flush()
    db.add(add_outbox_event(
        "contact_enquiry",
        enquiry.id,
        "forgeform.contact.created",
        {"contact_id": str(enquiry.id), "program": enquiry.interested_program, "source": enquiry.source},
        correlation_id,
    ))
    await queue_notification(
        db, enquiry.id, enquiry.email, "contact.received",
        "We received your enquiry",
        "Thank you for reaching out to Forge & Form. We received your enquiry and will follow up soon.",
        correlation_id,
    )
    await queue_notification(
        db, enquiry.id, settings.business_email, "contact.internal",
        "New Forge & Form contact enquiry",
        f"Name: {enquiry.full_name}\nEmail: {enquiry.email}\nPhone: {enquiry.phone}\n"
        f"Program: {enquiry.interested_program}\nGoals: {enquiry.fitness_goals}\n"
        f"Preferred contact: {enquiry.preferred_contact_method}\nMessage: {enquiry.message}",
        correlation_id,
    )
    await db.commit()
    return {"id": str(enquiry.id), "message": "Thanks for reaching out. We’ll be in touch."}


@router.get("/admin/contacts")
async def list_contacts(
    _user: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = (await db.scalars(select(ContactEnquiry).order_by(ContactEnquiry.created_at.desc()).limit(limit).offset(offset))).all()
    return [{"id": str(row.id), "name": row.full_name, "email": row.email, "phone": row.phone,
             "program": row.interested_program, "goals": row.fitness_goals, "preferredContact": row.preferred_contact_method,
             "message": row.message, "status": row.enquiry_status, "source": row.source,
             "createdAt": row.created_at.isoformat()} for row in rows]


@router.patch("/admin/contacts/{contact_id}/status")
async def set_contact_status(
    contact_id: UUID,
    body: ContactStatusUpdate,
    _user: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
):
    status_value = body.status
    enquiry = await db.get(ContactEnquiry, contact_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.enquiry_status = status_value
    db.add(add_outbox_event("contact_enquiry", enquiry.id, "forgeform.contact.updated",
                            {"contact_id": str(enquiry.id), "status": status_value}))
    await db.commit()
    return {"id": str(enquiry.id), "status": enquiry.enquiry_status}


@router.get("/admin/contacts/{contact_id}")
async def get_contact(contact_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    enquiry = await db.get(ContactEnquiry, contact_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return {"id": str(enquiry.id), "name": enquiry.full_name, "email": enquiry.email, "phone": enquiry.phone,
            "program": enquiry.interested_program, "goals": enquiry.fitness_goals,
            "preferredContact": enquiry.preferred_contact_method, "message": enquiry.message,
            "status": enquiry.enquiry_status, "source": enquiry.source}


@router.delete("/admin/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    enquiry = await db.get(ContactEnquiry, contact_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    await db.delete(enquiry)
    await db.commit()
