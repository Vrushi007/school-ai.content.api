<!--
This file is authored for AI coding agents (Copilot / Copilot Coding Agent).
Keep it concise and actionable — reference repository files and concrete patterns.
-->

# Copilot Instructions — Content Service API

Purpose: Help code-writing agents be immediately productive in this FastAPI + SQLAlchemy microservice.

1. Big picture

- **What**: A single FastAPI microservice that models hierarchical educational content (Board → State → Syllabus → Class → Subject → Chapter → KeyPoint → Session → Question).
- **Where**: `app/` contains the API surface (`app/main.py`, `app/routers/*`), domain models (`app/models/*`), business logic (`app/services/*`), and schemas (`app/schemas/*`).
- **DB layer**: SQLAlchemy declarative `app/db/base.py` + `app/db/session.py` (uses `DATABASE_URL` from `.env`). Alembic migrations live in `alembic/versions`.

2. Startup and common workflows (exact commands)

- Start services (Docker compose): `make up` or `docker compose up -d`.
- Local (no Docker): run `make setup-local`, then `source venv/bin/activate`, `alembic upgrade head`, and `uvicorn app.main:app --reload`.
- Run migrations (create): `docker compose exec content-service alembic revision --autogenerate -m "msg"` or `make migrate`.
- Apply migrations: `make upgrade` (`docker compose exec content-service alembic upgrade head`).
- Seed DB: `make seed-docker` (inside container) or `make seed` (local script `seed_data.py`).

3. Project-specific conventions and patterns

- Services implement business logic and operate on SQLAlchemy `Session` objects; routers call services and validate cross-entity constraints (example: `app/routers/chapters.py` checks `subject_service` before creating a chapter).
- Schemas are Pydantic v2 models. Use `.model_dump()` or `.model_dump(exclude_unset=True)` when converting for SQLAlchemy objects (see `app/services/chapter_service.py`).
- Database session is provided via dependency `get_db()` from `app/db/session.py`. Use `Depends(get_db)` in routers.
- Models use simple declarative classes under `app/models/`. Look at `app/models/chapter.py` for naming/field conventions (snake_case columns, `id` primary key).
- Seed ordering matters — `seed_data.py` inserts in dependency order (states → boards → syllabus → classes → subjects → chapters). Follow the same order for new seed files.

4. Error handling and HTTP conventions

- Routers raise `HTTPException(status_code, detail)` for not-found/validation errors (example: `chapters.create_chapter` raises 404 if subject missing).
- Create endpoints return `201` with response model; delete endpoints commonly return `204` with `None` body.

5. Testing and CI

- `make test` runs `pytest` inside Docker: `docker compose exec content-service pytest`.
- There are no visible unit tests in the repo root; when adding tests, prefer pytest and create lightweight fixtures that use a transactional DB or a test DB container.

6. Integration points & external dependencies

- Relies on PostgreSQL (`DATABASE_URL` env var). In Docker Compose the service is named `postgres` — check `docker-compose*.yml` for exact network/service names.
- Uses `pydantic-settings` (for settings) and `python-dotenv` (`load_dotenv` in `app/db/session.py`). Keep `.env` in sync with `.env.example`.

7. Typical code change patterns (examples)

- Adding a new resource (e.g., `Sequence`):
  - Add SQLAlchemy model in `app/models/` (use existing models for reference).
  - Add Pydantic schemas in `app/schemas/` (`Create`, `Update`, `Response`).
  - Add service functions in `app/services/` to encapsulate DB operations (return DB model instances, commit/refresh patterns shown in `chapter_service.py`).
  - Add router in `app/routers/` with dependency `db: Session = Depends(get_db)` and include it in `app/main.py`.
  - Add Alembic migration (use `alembic revision --autogenerate`) and `make upgrade`.

8. Quick code examples (copyable patterns)

- Creating and returning a DB object in a service:
  `db_obj = Model(**schema.model_dump())`
  `db.add(db_obj); db.commit(); db.refresh(db_obj); return db_obj`
- Partial updates:
  `update_data = schema.model_dump(exclude_unset=True)` then `setattr(db_obj, k, v)` for each field.

9. Files to inspect for guidance

- `app/main.py` — router registration, CORS, health endpoint.
- `app/routers/*.py` — route input validation and cross-service checks.
- `app/services/*.py` — DB interaction patterns and transaction handling.
- `app/db/session.py` — DB connection, `get_db()` dependency, pooling config.
- `seed_data.py` and `seed_data/*.json` — seeding order and data contract examples.
- `Makefile` — standard developer commands used in CI and local dev.

10. When in doubt

- Reproduce existing patterns exactly (service -> router -> schema -> model). Match response models and status codes used in nearby resources.
- Use `seed_data.py` patterns when adding or altering seed JSON formats.

If any part is unclear or you want specific examples (new resource implementation, a migration template, or a seed JSON example), tell me which area to expand and I'll update this file.
