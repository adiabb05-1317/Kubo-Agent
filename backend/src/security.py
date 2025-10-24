from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db_session
from .models import Session, User
from .settings import settings


pwd_context = CryptContext(schemes=[settings.password_scheme], deprecated="auto")


def hash_password(password: str) -> string:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def generate_token() -> str:
    return os.urandom(32).hex()


def hash_token(token: str) -> str:
    # Fast constant-time hash for storage; not reversible
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


async def create_session(
    *,
    db: AsyncSession,
    user: User,
    token: str,
    minutes: int,
    ip: Optional[str],
    user_agent: Optional[str],
) -> Session:
    token_h = hash_token(token)
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    sess = Session(user_id=user.id, token_hash=token_h, expires_at=expires, ip_address=ip, user_agent=user_agent)
    db.add(sess)
    await db.commit()
    await db.refresh(sess)
    return sess


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> User:
    cookie = request.cookies.get(settings.session_cookie_name)
    if not cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_h = hash_token(cookie)
    result = await db.execute(select(Session).where(Session.token_hash == token_h, Session.revoked == False))  # noqa: E712
    sess: Session | None = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid session")
    if sess.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user = await db.get(User, sess.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user


