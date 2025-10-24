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

### Initialize DB (create tables for dev)
```bash
python -m src.cli init-db
```

### Run the API
```bash
# option A: uvicorn directly
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# option B: console script (reads host/port from .env)
kubo-serve
```

### Environment
See `.env.example` for available settings. Default session cookie is `kubo_session`.


