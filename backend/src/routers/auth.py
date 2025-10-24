from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, Response, status

from ..schemas import LoginIn, UserCreate, UserOut
from ..security import generate_token, hash_password, hash_token, verify_password
from ..settings import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, request: Request) -> UserOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            "SELECT id, email, full_name, is_admin, is_active FROM users WHERE email = %s",
            (data.email,),
        )
        row = cur.fetchone()
        if row:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(data.password)
        cur.execute(
            """
            INSERT INTO users (email, full_name, hashed_password)
            VALUES (%s, %s, %s)
            RETURNING id, email, full_name, is_admin, is_active
            """,
            (data.email, data.full_name, hashed),
        )
        u = cur.fetchone()
        return UserOut.model_validate(
            {"id": u[0], "email": u[1], "full_name": u[2], "is_admin": u[3], "is_active": u[4]}
        )


@router.post("/login", response_model=UserOut)
async def login(data: LoginIn, response: Response, request: Request) -> UserOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            "SELECT id, email, full_name, hashed_password, is_admin, is_active FROM users WHERE email = %s",
            (data.email,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = {
            "id": row[0],
            "email": row[1],
            "full_name": row[2],
            "hashed_password": row[3],
            "is_admin": row[4],
            "is_active": row[5],
        }

        if not verify_password(data.password, user["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = generate_token()
        token_h = hash_token(token)
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.session_expire_minutes)
        cur.execute(
            """
            INSERT INTO sessions (user_id, token_hash, expires_at, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user["id"],
                token_h,
                expires,
                request.client.host if request.client else None,
                request.headers.get("user-agent"),
            ),
        )

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.samesite,
        max_age=settings.session_expire_minutes * 60,
        path="/",
    )
    return UserOut.model_validate(
        {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_admin": user["is_admin"],
            "is_active": user["is_active"],
        }
    )


@router.post("/logout")
async def logout(response: Response, request: Request) -> dict:
    cookie = request.cookies.get(settings.session_cookie_name)
    if cookie:
        token_h = hash_token(cookie)
        db_manager = request.app.state.db_manager
        with db_manager.cursor() as cur:
            cur.execute("UPDATE sessions SET revoked = TRUE WHERE token_hash = %s", (token_h,))
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(request: Request) -> UserOut:
    cookie = request.cookies.get(settings.session_cookie_name)
    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token_h = hash_token(cookie)
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            """
            SELECT u.id, u.email, u.full_name, u.is_admin, u.is_active, s.expires_at, s.revoked
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = %s
            """,
            (token_h,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
        expires_at = row[5]
        revoked = row[6]
        if revoked or expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

        return UserOut.model_validate(
            {
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "is_admin": row[3],
                "is_active": row[4],
            }
        )


@router.post("/seed", response_model=list[UserOut], status_code=201)
async def seed_users(request: Request) -> list[UserOut]:
    samples = [
        {"email": "admin@example.com", "full_name": "Admin User", "password": "AdminPass123", "is_admin": True},
        {"email": "guest@example.com", "full_name": "Guest User", "password": "GuestPass123", "is_admin": False},
    ]

    db_manager = request.app.state.db_manager
    created: list[UserOut] = []
    with db_manager.cursor() as cur:
        for sample in samples:
            hashed = hash_password(sample["password"])
            cur.execute(
                """
                INSERT INTO users (email, full_name, hashed_password, is_admin)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE
                SET full_name = EXCLUDED.full_name,
                    hashed_password = EXCLUDED.hashed_password,
                    is_admin = EXCLUDED.is_admin,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, email, full_name, is_admin, is_active
                """,
                (sample["email"], sample["full_name"], hashed, sample["is_admin"]),
            )
            row = cur.fetchone()
            created.append(
                UserOut.model_validate(
                    {
                        "id": row[0],
                        "email": row[1],
                        "full_name": row[2],
                        "is_admin": row[3],
                        "is_active": row[4],
                    }
                )
            )
    return created


