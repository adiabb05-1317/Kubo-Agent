from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from psycopg2 import errors

from ..schemas import (
    BookingCreate,
    BookingOut,
    BookingUpdate,
    BookingStatus,
    PodCreate,
    PodOut,
    PodUpdate,
)


router = APIRouter(prefix="/kubo", tags=["kubo"])


def _pod_from_row(row: tuple[Any, ...]) -> PodOut:
    return PodOut.model_validate(
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "capacity": row[3],
            "price_cents": row[4],
            "is_active": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }
    )


def _booking_from_row(row: tuple[Any, ...]) -> BookingOut:
    return BookingOut.model_validate(
        {
            "id": row[0],
            "user_id": row[1],
            "pod_id": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "status": BookingStatus(row[5]) if not isinstance(row[5], BookingStatus) else row[5],
            "total_price_cents": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }
    )


@router.get("/pods", response_model=list[PodOut])
async def list_pods(request: Request) -> list[PodOut]:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, description, capacity, price_cents, is_active, created_at, updated_at
            FROM pods
            ORDER BY name
            """
        )
        rows = cur.fetchall()
    return [_pod_from_row(row) for row in rows]


@router.get("/pods/{pod_id}", response_model=PodOut)
async def get_pod(pod_id: int, request: Request) -> PodOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            """
            SELECT id, name, description, capacity, price_cents, is_active, created_at, updated_at
            FROM pods
            WHERE id = %s
            """,
            (pod_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pod not found")
    return _pod_from_row(row)


# --- Pod routes (admin only) ---
@router.post("/pods", response_model=PodOut, status_code=status.HTTP_201_CREATED)
async def create_pod(data: PodCreate, request: Request) -> PodOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO pods (name, description, capacity, price_cents, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, description, capacity, price_cents, is_active, created_at, updated_at
                """,
                (data.name, data.description, data.capacity, data.price_cents, data.is_active),
            )
        except errors.UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pod name already exists")
        row = cur.fetchone()
    return _pod_from_row(row)


@router.patch("/pods/{pod_id}", response_model=PodOut)
async def update_pod(pod_id: int, data: PodUpdate, request: Request) -> PodOut:
    updates: list[str] = []
    params: list[Any] = []

    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    if data.description is not None:
        updates.append("description = %s")
        params.append(data.description)
    if data.capacity is not None:
        updates.append("capacity = %s")
        params.append(data.capacity)
    if data.price_cents is not None:
        updates.append("price_cents = %s")
        params.append(data.price_cents)
    if data.is_active is not None:
        updates.append("is_active = %s")
        params.append(data.is_active)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    updates.append("updated_at = CURRENT_TIMESTAMP")

    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        try:
            cur.execute(
                f"""
                UPDATE pods
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, name, description, capacity, price_cents, is_active, created_at, updated_at
                """,
                (*params, pod_id),
            )
        except errors.UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pod name already exists")
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pod not found")
    return _pod_from_row(row)


@router.delete("/pods/{pod_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pod(pod_id: int, request: Request) -> Response:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute("DELETE FROM pods WHERE id = %s RETURNING id", (pod_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pod not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Booking routes (user accessible) ---
@router.get("/bookings", response_model=list[BookingOut])
async def list_bookings(request: Request) -> list[BookingOut]:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            """
            SELECT id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
            FROM bookings
            ORDER BY start_time DESC
            """
        )
        rows = cur.fetchall()
    return [_booking_from_row(row) for row in rows]


@router.get("/bookings/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, request: Request) -> BookingOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute(
            """
            SELECT id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
            FROM bookings
            WHERE id = %s
            """,
            (booking_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _booking_from_row(row)


@router.post("/bookings", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(data: BookingCreate, request: Request) -> BookingOut:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO bookings (user_id, pod_id, start_time, end_time, status, total_price_cents)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                """,
                (
                    data.user_id,
                    data.pod_id,
                    data.start_time,
                    data.end_time,
                    data.status.value if isinstance(data.status, BookingStatus) else data.status,
                    data.total_price_cents,
                ),
            )
        except errors.UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already exists for this time window")
        row = cur.fetchone()
    return _booking_from_row(row)


@router.patch("/bookings/{booking_id}", response_model=BookingOut)
async def update_booking(booking_id: int, data: BookingUpdate, request: Request) -> BookingOut:
    updates: list[str] = []
    params: list[Any] = []

    if data.start_time is not None:
        updates.append("start_time = %s")
        params.append(data.start_time)
    if data.end_time is not None:
        updates.append("end_time = %s")
        params.append(data.end_time)
    if data.status is not None:
        updates.append("status = %s")
        params.append(data.status.value if isinstance(data.status, BookingStatus) else data.status)
    if data.total_price_cents is not None:
        updates.append("total_price_cents = %s")
        params.append(data.total_price_cents)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    updates.append("updated_at = CURRENT_TIMESTAMP")

    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        try:
            cur.execute(
                f"""
                UPDATE bookings
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, user_id, pod_id, start_time, end_time, status, total_price_cents, created_at, updated_at
                """,
                (*params, booking_id),
            )
        except errors.UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already exists for this time window")
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return _booking_from_row(row)


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, request: Request) -> Response:
    db_manager = request.app.state.db_manager
    with db_manager.cursor() as cur:
        cur.execute("DELETE FROM bookings WHERE id = %s RETURNING id", (booking_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


