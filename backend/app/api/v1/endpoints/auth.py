from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import current_user
from app.core.security import (
    hash_refresh_token, make_access_token, make_refresh_token, verify_password,
)
from app.database.session import get_db
from app.models import RefreshToken, User
from app.schemas import LoginRequest, RefreshRequest

router = APIRouter()


def refresh_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == request.email.lower()))
    if user is None or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = make_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=hash_refresh_token(token), expires_at=refresh_expiry()))
    await db.commit()
    return {
        "access_token": make_access_token(user.id),
        "refresh_token": token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    stored = await db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(request.refresh_token))
        .with_for_update()
    )
    now = datetime.now(timezone.utc)
    if stored is None or stored.revoked_at is not None or stored.expires_at <= now:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = await db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive account")
    replacement_value = make_refresh_token()
    replacement = RefreshToken(user_id=user.id, token_hash=hash_refresh_token(replacement_value), expires_at=refresh_expiry())
    db.add(replacement)
    await db.flush()
    stored.revoked_at = now
    stored.replaced_by_id = replacement.id
    await db.commit()
    return {"access_token": make_access_token(user.id), "refresh_token": replacement_value, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    stored = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(request.refresh_token)))
    if stored is not None and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        await db.commit()


@router.get("/me")
async def me(user: User = Depends(current_user)):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "roles": [role.name for role in user.roles],
    }
