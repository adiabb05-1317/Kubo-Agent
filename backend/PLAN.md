# Backend Build Plan (FastAPI + PostgreSQL)

This plan tracks the high-level tasks to build the backend shown in the architecture diagram. We will implement cookie-based auth, booking domain models, and APIs. We will use `uv` for environment and dependency management.

## Scope for Phase 1 (finish DB and auth API)
- [x] Create project scaffold with FastAPI app skeleton and `pyproject.toml`
- [ ] Configure async PostgreSQL engine/session and env-based settings
- [ ] Define SQLAlchemy models: `User`, `Pod`, `Booking`, `Session`
- [ ] Implement cookie-based auth: password hashing, session tokens, dependencies
- [ ] Auth API endpoints: register, login, logout, current user
- [ ] App wiring, CORS, lifespan checks, and local run instructions

## Phase 2 (booking and pods API)
- [ ] Pods CRUD (admin-restricted for write ops)
- [ ] Bookings: availability, create, list my bookings, cancel
- [ ] Realtime updater (stub/event hooks)
- [ ] Alembic migrations

Notes
- Security: HttpOnly session cookie, optional `Secure` with `COOKIE_SECURE` setting, rotate tokens on login, server-side invalidation on logout/expiry.
- Time: all timestamps are stored in UTC.


