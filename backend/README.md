## Backend (FastAPI + PostgreSQL)

### Prereqs
- Python 3.11+
- PostgreSQL running and accessible
- [`uv`](https://github.com/astral-sh/uv) installed

### Setup
```bash
cd backend
cp .env.example .env
# update .env to point to your Postgres

uv venv
source .venv/bin/activate
uv pip install -e .
```

### Initialize database
The backend now ships with SQL scripts for schema + demo data. Run them against your local Postgres after it is running.

```bash
# apply schema (tables, enums, triggers)
psql -h 127.0.0.1 -U kubo_user -d kubodb -f backend/sql/migrations.sql

# optional demo seed (users, pods, bookings)
psql -h 127.0.0.1 -U kubo_user -d kubodb -f backend/sql/seed_data.sql
```

> Tip: if you are running Postgres via docker compose, replace the command with `docker compose exec db psql -U kubo_user -d kubodb -f /app/backend/sql/migrations.sql` (copy the file into the container first or mount the repo).

### Run the API
```bash
# fastest local loop
uv run main.py

# or use uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Environment
See `.env.example` for available settings. Default session cookie is `kubo_session`.


