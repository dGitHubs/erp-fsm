# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python/FastAPI)

```bash
uv sync                                          # install dependencies
uv run uvicorn app.main:app --reload             # start dev server (requires .env)
uv run pytest                                    # run all tests
uv run pytest tests/test_manufacturing_orders.py # run a single test file
uv run pytest -k "test_create"                   # run tests matching a pattern
uv run ruff check .                              # lint
uv run ruff format .                             # format
```

### Database

```bash
docker compose up -d                             # start PostgreSQL on port 5433
uv run alembic upgrade head                      # apply migrations
uv run alembic revision --autogenerate -m "..."  # generate a new migration
```

### Frontend (React/Vite)

```bash
cd erp-fsm-web
npm install
npm run dev                                      # dev server (proxies to localhost:8000)
npm run build                                    # production build
npm run lint                                     # ESLint
```

## Environment

The backend requires a `.env` file at the project root:

```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/erp_fsm
SECRET_KEY=<any string>
```

## Architecture

### Backend layers

Each domain (customers, products, materials, product_materials, manufacturing_orders) follows the same four-layer pattern:

- `app/models/<domain>.py` — SQLAlchemy ORM model, inherits `Base` from `app/db.py`
- `app/schemas/<domain>.py` — Pydantic v2 schemas (`*Create`, `*Response`); use `model_config = ConfigDict(from_attributes=True)` on response schemas
- `app/services/<domain>.py` — all business logic and DB queries; raises typed domain exceptions (e.g. `CustomerNotFoundError`) rather than HTTP exceptions
- `app/routes/<domain>.py` — thin FastAPI router; catches domain exceptions and maps them to `HTTPException`

Routers are registered in `app/routes/__init__.py` and included in `app/main.py`.

Settings are loaded from `.env` via `app/config.py` (pydantic-settings); access them as `from app.config import settings`.

### Key business logic

`app/services/manufacturing_order.py` contains the planning logic:
- **Material requirements**: `BOM quantity × order quantity` per material
- **Material availability**: compares requirements against `material.quantity_on_hand`; sets `can_produce=False` if any material is short

`ProductMaterial` (the BOM join table) has a unique constraint on `(product_id, material_id)`.

### Tests

Tests run against a real PostgreSQL database (`erp_fsm_test` on port 5433 — start it with `docker compose up -d`, then create it once with `PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE erp_fsm_test;"`). Tables are created once per test session; each test runs inside a transaction that is rolled back at the end, so tests are isolated without recreating the schema. The `client` fixture overrides FastAPI's `get_db` dependency to inject the same transactional session.

All new models must be imported in `tests/conftest.py` (`from app import models`) so `Base.metadata.create_all` picks them up — the `models/__init__.py` must re-export them.

### Frontend

The React frontend lives in `erp-fsm-web/` (React 19, Vite, TypeScript). It is a scaffold; API calls go through `src/api/client.ts` (`apiFetch`) pointing to `http://localhost:8000`. TypeScript types mirroring the API responses live in `src/types/`.