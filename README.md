# Kubo Booking Application

Modern pods booking app with FastAPI + PostgreSQL and a Next.js frontend with Zustand. Includes an AI concierge powered by Cerebras with tool-calling for pods and bookings.

![Kubo Booking Application](./images/diagram.png)

## Stack
- Backend: FastAPI, psycopg2, Pydantic v2
- DB: PostgreSQL (Docker Compose included)
- Frontend: Next.js (client components), Zustand
- AI: Cerebras Cloud SDK with tool calling

## Quick Start

### 1) Start PostgreSQL (Docker Compose)

From repo root:

```bash
docker compose up -d db
```

Default credentials (see `docker-compose.yml`):
- user: `kubo_user`
- password: `password`
- database: `kubodb`
- port: `5432`

### 2) Initialize the database schema and seed data

Once Postgres is up, apply migrations and optional seed data.

Using local psql:
```bash
psql -h 127.0.0.1 -U kubo_user -d kubodb -f backend/sql/migrations.sql
psql -h 127.0.0.1 -U kubo_user -d kubodb -f backend/sql/seed_data.sql
```

If you prefer docker exec (container name `postgres_dev` from compose):
```bash
docker exec -i postgres_dev psql -U kubo_user -d kubodb < backend/sql/migrations.sql
docker exec -i postgres_dev psql -U kubo_user -d kubodb < backend/sql/seed_data.sql
```

### 3) Run the Backend API

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .

# run
uv run main.py
# or
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Environment variables (`backend/src/settings.py`):
- `DATABASE_URL` style DSN is not required; code uses `Settings.database_url` default: `postgresql://kubo_user:password@127.0.0.1:5432/kubodb`
- CORS defaults to `http://localhost:3000`
- Session cookie name: `kubo_session`

### 4) Run the Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend expects the backend at `http://127.0.0.1:8000` (can override via `NEXT_PUBLIC_API_URL`).

### 5) AI Concierge (optional)

If you have a Cerebras API key, set it (optional, module is resilient if not set):
```bash
export CEREBRAS_API_KEY=your-key
```

Endpoints:
- `GET /ai/models` – list models
- `GET /ai/tools` – list registered tools
- `POST /ai/chat/auto` – tool-calling loop; persists conversation in `chat_history`
- `GET /ai/history` – latest conversation for the logged-in user

### Useful Endpoints
- Auth: `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`
- Pods: `/kubo/pods`, `/kubo/pods/{id}`
- Bookings: `/kubo/bookings`, `/kubo/bookings/{id}`, `POST /kubo/bookings`

## Notes
- Passwords are stored as plain text per simplified dev requirement. Do NOT use in production.
- If you change DB creds, update `backend/src/settings.py` or `.env`.