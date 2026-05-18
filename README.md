# ERP Fabrication Sur Mesure

Socle initial d'une application interne pour la gestion de fabrication sur mesure.

## Stack
- Python 3.12+
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic
- Pydantic v2
- Jinja2
- PyYAML
- uv

## Lancer le projet

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Vérification rapide

Ouvrir :

```text
http://127.0.0.1:8000/health
```
