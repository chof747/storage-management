# Current SQLite Analysis

This document captures the Phase 0 baseline analysis for the PostgreSQL migration.

Date: 2026-04-01
Scope: Task 0.1 (inventory) and Task 0.2 (technical decisions)

---

## 1) Current DB integration inventory (Task 0.1)

### 1.1 Engine and session wiring

- Engine creation: `backend/app/database.py`
  - `SQLALCHEMY_DATABASE_URL` defaults to `sqlite:///./test.db`
  - engine is created with unconditional `connect_args={"check_same_thread": False}`
- Session provider: `backend/app/dependencies.py`
  - `get_db()` yields `SessionLocal()` and closes it in `finally`

### 1.2 SQLite path and URL configuration points

- `backend/.env`
  - `DATABASE_URL=sqlite:///../data/backend/test.db`
- `docker-compose.yml`
  - backend env sets `DATABASE_URL=sqlite:////data/test.db`
- `backend/tests/conftest.py`
  - builds `APITEST_DATABASE_URL` as either file-based SQLite or `sqlite:///:memory:`
- `backend/db_migrations/env.py` (renamed from `backend/alembic/env.py`)
  - fallback URL is `sqlite:////data/app.db`

### 1.3 Schema creation paths

- `backend/app/init.py`
  - `Base.metadata.create_all(bind=engine)`
- `backend/tests/conftest.py`
  - `Base.metadata.drop_all(...)` and `Base.metadata.create_all(...)`
- `backend/docker/entrypoint.sh`
  - runs `pdm run migrate` (Alembic `upgrade head`) on container startup

### 1.4 Alembic files

- `backend/alembic.ini`
- `backend/db_migrations/env.py`
- `backend/db_migrations/script.py.mako`
- `backend/db_migrations/migration_test.sh`
- `backend/db_migrations/versions/*.py`

### 1.5 Test DB fixtures and seed setup

- `backend/tests/conftest.py`
- `backend/tests/utils/db_seed_loader.py`
- `backend/tests/seeds/storage_type.csv`
- `backend/tests/seeds/storage_element.csv`
- `backend/tests/seeds/hardware_items.csv`

### 1.6 CI/container/deployment baseline

- Test CI workflow: `.github/workflows/test_backend.yml`
  - no PostgreSQL service container yet
- Runtime compose: `docker-compose.yml`
  - backend and frontend services; backend uses SQLite URL
- Image build workflow: `.github/workflows/build_docker.yml`
- Backend runtime image: `backend/Dockerfile` + `backend/docker/entrypoint.sh`

### 1.7 SQLite-specific assumptions identified

- SQLite defaults are embedded in app config, Alembic fallback, tests, and compose runtime.
- Engine creation always includes SQLite-only `check_same_thread` option.
- Tests rely on SQLite semantics (`:memory:` and metadata create/drop pattern).
- `backend/db_migrations/migration_test.sh` assumes `DATABASE_URL` is a SQLite file URL and strips `sqlite:///`.
- Variable mismatch in test config:
  - `backend/.env` uses `APITEST__DATABASE_PATH`
  - `backend/tests/conftest.py` reads `APITEST_DATABASE_PATH`

---

## 2) Confirmed technical decisions (Task 0.2)

- PostgreSQL version: 16
- PostgreSQL driver: `psycopg` v3
- Canonical DB env strategy: single `DATABASE_URL` across app, Alembic, tests, and deployment
- Dedicated app schema strategy: `DB_SCHEMA` (default `storage_management`) for non-public PostgreSQL namespace isolation
- Local development strategy: externally managed local Docker Compose PostgreSQL service (shared across projects), with this repository connecting via `DATABASE_URL` only
- Test orchestration strategy: self-contained PostgreSQL for tests in both environments (local: `docker-compose.test.yml`, CI: GitHub Actions `services`) + Alembic schema init before tests
- Alembic history strategy: preserve current migration history first; only rebase if PostgreSQL validation shows blockers
- Migration tool location: `backend/tools/sqlite_to_postgres.py` (or split helpers under `backend/tools/`)

---

## 3) Phase 0 completion check

- [x] All DB-relevant files identified
- [x] SQLite-specific assumptions documented
- [x] No open design blockers for Phase 1 implementation
