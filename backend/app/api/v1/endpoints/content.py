from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import BlogCategory, BlogPost, Location, Notification, Program, ProgramCategory, Testimonial, Trainer, User
from app.schemas import BlogWrite, LocationWrite, ProgramWrite, TestimonialWrite, TrainerWrite
from app.services.outbox import add_outbox_event

router = APIRouter()
admin = require_roles("ADMIN", "SUPER_ADMIN", "STAFF")


def program_view(row: Program) -> dict:
    return {
        "id": str(row.id), "slug": row.slug, "title": row.name, "eyebrow": row.category.name,
        "summary": row.short_description, "description": row.description, "image": row.image_url,
        "alt": row.name, "benefits": row.benefits, "suitableFor": row.target_audience,
    }


def trainer_view(row: Trainer) -> dict:
    experience = f"{row.experience_years} years of experience" if row.experience_years is not None else "Experience details to be confirmed"
    return {
        "id": str(row.id), "slug": row.slug, "name": row.full_name, "title": row.designation,
        "image": row.profile_image, "alt": row.full_name, "bio": row.biography,
        "specialties": row.specializations, "experience": experience,
    }


def blog_view(row: BlogPost) -> dict:
    published = row.published_at
    return {
        "id": str(row.id), "slug": row.slug, "title": row.title, "category": row.category.name,
        "excerpt": row.excerpt, "content": row.content, "image": row.featured_image,
        "alt": row.title, "author": row.author_name,
        "date": published.date().isoformat() if published else "",
        "readingTime": row.reading_time,
    }


def location_view(row: Location) -> dict:
    return {
        "id": str(row.id), "name": row.name, "address": row.address, "city": row.city, "state": row.state,
        "postal_code": row.postal_code, "country": row.country, "phone": row.phone, "email": row.email,
        "latitude": row.latitude, "longitude": row.longitude, "opening_hours": row.opening_hours,
    }


@router.get("/programs")
async def list_programs(
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Program).where(Program.is_active.is_(True)).order_by(Program.display_order, Program.name)
    if search:
        query = query.where(or_(Program.name.ilike(f"%{search}%"), Program.short_description.ilike(f"%{search}%")))
    rows = (await db.scalars(query.limit(limit).offset(offset))).all()
    return [program_view(row) for row in rows]


@router.get("/program-categories")
async def list_program_categories(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(ProgramCategory).order_by(ProgramCategory.name))).all()
    return [{"id": str(row.id), "name": row.name, "slug": row.slug} for row in rows]


@router.get("/programs/{slug}")
async def get_program(slug: str, db: AsyncSession = Depends(get_db)):
    row = await db.scalar(select(Program).where(Program.slug == slug, Program.is_active.is_(True)))
    if row is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return program_view(row)


@router.post("/admin/programs", status_code=201)
async def create_program(request: ProgramWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    values = request.model_dump()
    category = await db.scalar(select(ProgramCategory).where(ProgramCategory.name == values.pop("category")))
    if category is None:
        raise HTTPException(status_code=422, detail="Choose a configured program category")
    row = Program(**values, category=category)
    db.add(row)
    await db.flush()
    db.add(add_outbox_event("program", row.id, "forgeform.program.updated", {"program_id": str(row.id)}))
    await db.commit()
    return program_view(row)


@router.put("/admin/programs/{program_id}")
async def update_program(program_id: UUID, request: ProgramWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Program, program_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Program not found")
    values = request.model_dump()
    category = await db.scalar(select(ProgramCategory).where(ProgramCategory.name == values.pop("category")))
    if category is None:
        raise HTTPException(status_code=422, detail="Choose a configured program category")
    for key, value in values.items():
        setattr(row, key, value)
    row.category = category
    db.add(add_outbox_event("program", row.id, "forgeform.program.updated", {"program_id": str(row.id)}))
    await db.commit()
    return program_view(row)


@router.delete("/admin/programs/{program_id}", status_code=204)
async def delete_program(program_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Program, program_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Program not found")
    row.is_active = False
    await db.commit()


@router.get("/trainers")
async def list_trainers(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Trainer).where(Trainer.is_active.is_(True)).order_by(Trainer.full_name))).all()
    return [trainer_view(row) for row in rows]


@router.get("/trainers/{slug}")
async def get_trainer(slug: str, db: AsyncSession = Depends(get_db)):
    row = await db.scalar(select(Trainer).where(Trainer.slug == slug, Trainer.is_active.is_(True)))
    if row is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer_view(row)


@router.post("/admin/trainers", status_code=201)
async def create_trainer(request: TrainerWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = Trainer(**request.model_dump())
    db.add(row)
    await db.flush()
    db.add(add_outbox_event("trainer", row.id, "forgeform.trainer.updated", {"trainer_id": str(row.id)}))
    await db.commit()
    return trainer_view(row)


@router.put("/admin/trainers/{trainer_id}")
async def update_trainer(trainer_id: UUID, request: TrainerWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Trainer, trainer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    for key, value in request.model_dump().items():
        setattr(row, key, value)
    db.add(add_outbox_event("trainer", row.id, "forgeform.trainer.updated", {"trainer_id": str(row.id)}))
    await db.commit()
    return trainer_view(row)


@router.delete("/admin/trainers/{trainer_id}", status_code=204)
async def delete_trainer(trainer_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Trainer, trainer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Trainer not found")
    row.is_active = False
    await db.commit()


@router.get("/testimonials")
async def list_testimonials(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Testimonial).where(Testimonial.is_published.is_(True)).order_by(Testimonial.created_at.desc()))).all()
    return [{"id": str(row.id), "name": row.customer_name, "quote": row.content, "image": row.customer_image} for row in rows]


@router.get("/admin/testimonials")
async def list_all_testimonials(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Testimonial).order_by(Testimonial.created_at.desc()))).all()
    return [{"id": str(row.id), "customer_name": row.customer_name, "customer_image": row.customer_image,
             "content": row.content, "rating": row.rating, "program_id": str(row.program_id) if row.program_id else None,
             "is_published": row.is_published} for row in rows]


@router.get("/admin/notifications")
async def admin_notifications(
    _user: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = (await db.scalars(
        select(Notification).order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    )).all()
    return [{
        "id": str(row.id), "recipient": row.recipient, "notification_type": row.notification_type,
        "subject": row.subject, "status": row.status, "retry_count": row.retry_count,
        "created_at": row.created_at.isoformat(),
        "sent_at": row.sent_at.isoformat() if row.sent_at else None,
    } for row in rows]


@router.post("/admin/testimonials", status_code=201)
async def create_testimonial(request: TestimonialWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = Testimonial(**request.model_dump())
    db.add(row)
    await db.commit()
    return {"id": str(row.id)}


@router.put("/admin/testimonials/{testimonial_id}")
async def update_testimonial(testimonial_id: UUID, request: TestimonialWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Testimonial, testimonial_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    for key, value in request.model_dump().items():
        setattr(row, key, value)
    await db.commit()
    return {"id": str(row.id)}


@router.delete("/admin/testimonials/{testimonial_id}", status_code=204)
async def delete_testimonial(testimonial_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Testimonial, testimonial_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    await db.delete(row)
    await db.commit()


@router.get("/blog")
async def list_blog(
    search: str | None = None,
    category: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(BlogPost).join(BlogCategory).where(
        BlogPost.is_published.is_(True), BlogPost.published_at.is_not(None), BlogPost.published_at <= datetime.now(timezone.utc)
    )
    if search:
        query = query.where(or_(BlogPost.title.ilike(f"%{search}%"), BlogPost.excerpt.ilike(f"%{search}%")))
    if category:
        query = query.where(BlogCategory.slug == category)
    rows = (await db.scalars(query.order_by(BlogPost.published_at.desc()).limit(limit).offset(offset))).all()
    return [blog_view(row) for row in rows]


@router.get("/blog/categories")
async def blog_categories(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(BlogCategory).order_by(BlogCategory.name))).all()
    return [{"id": str(row.id), "name": row.name, "slug": row.slug} for row in rows]


@router.get("/blog/{slug}")
async def get_blog(slug: str, db: AsyncSession = Depends(get_db)):
    row = await db.scalar(select(BlogPost).where(BlogPost.slug == slug, BlogPost.is_published.is_(True),
                                                 BlogPost.published_at.is_not(None), BlogPost.published_at <= datetime.now(timezone.utc)))
    if row is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return blog_view(row)


@router.get("/admin/blog")
async def admin_blog(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(BlogPost).order_by(BlogPost.created_at.desc()))).all()
    return [blog_view(row) | {"is_published": row.is_published} for row in rows]


@router.post("/admin/blog", status_code=201)
async def create_blog(request: BlogWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    values = request.model_dump()
    if values["is_published"] and values["published_at"] is None:
        values["published_at"] = datetime.now(timezone.utc)
    row = BlogPost(**values)
    db.add(row)
    await db.commit()
    return {"id": str(row.id), "slug": row.slug}


@router.put("/admin/blog/{post_id}")
async def update_blog(post_id: UUID, request: BlogWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(BlogPost, post_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Article not found")
    values = request.model_dump()
    if values["is_published"] and values["published_at"] is None:
        values["published_at"] = datetime.now(timezone.utc)
    for key, value in values.items():
        setattr(row, key, value)
    await db.commit()
    return {"id": str(row.id), "slug": row.slug}


@router.delete("/admin/blog/{post_id}", status_code=204)
async def delete_blog(post_id: UUID, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(BlogPost, post_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await db.delete(row)
    await db.commit()


@router.get("/locations")
async def list_locations(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Location).where(Location.is_active.is_(True)).order_by(Location.name))).all()
    return [location_view(row) for row in rows]


@router.get("/locations/{location_id}")
async def get_location(location_id: UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(Location, location_id)
    if row is None or not row.is_active:
        raise HTTPException(status_code=404, detail="Location not found")
    return location_view(row)


@router.get("/admin/locations")
async def admin_locations(_user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Location).order_by(Location.name))).all()
    return [location_view(row) for row in rows]


@router.post("/admin/locations", status_code=201)
async def create_location(request: LocationWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = Location(**request.model_dump())
    db.add(row)
    await db.commit()
    return {"id": str(row.id)}


@router.put("/admin/locations/{location_id}")
async def update_location(location_id: UUID, request: LocationWrite, _user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(Location, location_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in request.model_dump().items():
        setattr(row, key, value)
    await db.commit()
    return {"id": str(row.id)}
