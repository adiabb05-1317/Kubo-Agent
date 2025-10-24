from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from ..models import Session, User
from ..schemas import LoginIn, UserCreate, UserOut
from ..security import create_session, generate_token, hash_password, verify_password
from ..settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db_session)) -> UserOut:
    exists = await db.execute(select(User).where(User.email == data.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, full_name=data.full_name, hashed_password=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.samesite,  # type: ignore[arg-type]
        max_age=settings.session_expire_minutes * 60,
        path="/",
    )


@router.post("/login", response_model=UserOut)
async def login(
    data: LoginIn,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> UserOut:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = generate_token()
    await create_session(
        db=db,
        user=user,
        token=token,
        minutes=settings.session_expire_minutes,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    set_session_cookie(response, token)
    return UserOut.model_validate(user)


@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_db_session)) -> dict:
    cookie = request.cookies.get(settings.session_cookie_name)
    if cookie:
        # Revoke session if present
        from ..security import hash_token

        token_h = hash_token(cookie)
        result = await db.execute(select(Session).where(Session.token_hash == token_h))
        sess = result.scalar_one_or_none()
        if sess:
            sess.revoked = True
            await db.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(request: Request, db: AsyncSession = Depends(get_db_session)) -> UserOut:
    from ..security import get_current_user

    user = await get_current_user(request, db)
    return UserOut.model_validate(user)


