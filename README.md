# ERP Fabrication Sur Mesure

## Setup

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up
```

## Tests

```bash
uv run pytest
```
