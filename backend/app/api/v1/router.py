from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, content, contacts, marketing

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(content.router, tags=["content"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(bookings.admin_router, tags=["admin bookings"])
api_router.include_router(contacts.router, tags=["contact"])
api_router.include_router(marketing.router, prefix="/marketing-events", tags=["analytics"])
api_router.include_router(marketing.analytics_router, tags=["admin analytics"])
