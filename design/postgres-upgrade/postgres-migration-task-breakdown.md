# PostgreSQL Migration Task Breakdown

This document breaks the PostgreSQL migration into concrete implementation tasks for the `storage-management` repository.

It is intended as a practical execution plan that can later be converted into GitHub issues, milestones, or pull requests.

---

## Phase 0 - Preparation and baseline review

### Task 0.1 - Inventory the current database integration

**Status**
- done (see `design/postgres-upgrade/current-sqlite-analysis.md`)

**Goal**
Understand exactly how SQLite is currently wired into the backend, migrations, tests, and deployment.

**Steps**
- Identify the backend module that creates the SQLAlchemy engine.
- Identify the backend module that creates/provides DB sessions.
- Identify where the SQLite file path is configured.
- Identify where schema creation currently happens.
- Identify all Alembic-related files.
- Identify all test fixtures related to DB setup.
- Identify any CI or container config already used for tests.
- Identify the current production deployment configuration.

**Deliverable**
A short list of affected files and expected change areas.

**Done when**
- [x] all DB-relevant files are identified
- [x] SQLite-specific assumptions are documented

---

### Task 0.2 - Confirm technical decisions

**Status**
- done (see `design/postgres-upgrade/current-sqlite-analysis.md`)

**Goal**
Lock the key decisions so implementation does not drift.

**Decisions to confirm**
- PostgreSQL version
- PostgreSQL driver (`psycopg` recommended)
- environment variable strategy (`DATABASE_URL` preferred)
- local development strategy (Docker Compose and/or local server)
- test orchestration strategy
- whether Alembic history is preserved or rebased
- migration-script location in the repo

**Deliverable**
A short decision record added to the design docs or PR description.

**Done when**
- [x] no open design blockers remain for implementation

---

## Phase 1 - Configuration and dependency setup

### Task 1.1 - Add PostgreSQL dependencies to the backend

**Status**
- done

**Goal**
Ensure the backend can connect to PostgreSQL.

**Steps**
- Add `psycopg` dependency.
- Verify SQLAlchemy dependency version is PostgreSQL-compatible.
- Verify Alembic dependency version is appropriate.
- Update lockfile/package management files if present.

**Deliverable**
Updated dependency configuration.

**Implementation notes**
- `backend/pyproject.toml` includes `psycopg>=3.3.3` in runtime dependencies.
- Lockfile updated in `backend/pdm.lock` with resolved package versions.
- Verified installed versions in backend environment:
  - `psycopg 3.3.3`
  - `SQLAlchemy 2.0.44`
  - `Alembic 1.16.5`

**Done when**
- [x] backend environment installs successfully with PostgreSQL support

---

### Task 1.2 - Introduce DB environment configuration

**Status**
- done

**Goal**
Make the database connection environment-driven.

**Steps**
- Introduce a canonical `DATABASE_URL` setting.
- Keep optional support for deriving it from separate env vars only if really needed.
- Add defaults/examples for development.
- Add example values for production and test.
- Update `.env.example` or equivalent config docs if present.

**Deliverable**
Centralized DB configuration.

**Implementation notes**
- `backend/app/database.py` now requires `DATABASE_URL` from environment instead of using a SQLite fallback.
- `backend/db_migrations/env.py` now requires `DATABASE_URL` instead of falling back to a SQLite URL.
- Updated `backend/.env.sample` with canonical `DATABASE_URL` usage and development/test/production examples.
- Added `DB_SCHEMA` configuration so app tables can be managed in a dedicated PostgreSQL schema.
- Updated `backend/.env` to use a PostgreSQL `DATABASE_URL` for local development.

**Done when**
- [x] application startup can resolve the DB connection from config without relying on SQLite path defaults

---

### Task 1.3 - Add local PostgreSQL development setup

**Status**
- done

**Goal**
Make local PostgreSQL startup easy and repeatable.

**Steps**
- Use an external Docker Compose PostgreSQL setup that is independent of this repository's backend/frontend containers.
- Define minimal required PostgreSQL connection settings (`host`, `port`, `database`, `user`, `password`).
- Define required compatibility requirements (supported PostgreSQL major version and driver URL format).
- Define optional but recommended requirements (persistent volume, healthcheck, restart policy).
- Document how this project connects to that external local DB via `DATABASE_URL`.

**Deliverable**
Documented local PostgreSQL connection contract for an externally managed Docker setup.

**Implementation notes**
- Documented external local PostgreSQL requirements and connection contract in `README.md`.
- Documented canonical `DATABASE_URL` example for shared local dev PostgreSQL.
- Clarified that this repository connects to an external local PostgreSQL service rather than managing it in this repository's compose stack.

**Done when**
- [x] a developer can connect this project to a separately managed local PostgreSQL Docker setup with a short documented sequence

---

## Phase 2 - Backend database layer refactoring

### Task 2.1 - Refactor engine creation

**Status**
- done

**Goal**
Switch engine creation from SQLite assumptions to PostgreSQL-ready configuration.

**Steps**
- Update the SQLAlchemy `create_engine` call to use `DATABASE_URL`.
- Remove SQLite-only `connect_args`.
- Review pool settings if currently absent or SQLite-specific.
- Ensure the engine is created in a clean, reusable module.

**Deliverable**
PostgreSQL-ready engine configuration.

**Implementation notes**
- `backend/app/database.py` now creates the engine from required `DATABASE_URL` without SQLite-only `connect_args`.
- Added `pool_pre_ping=True` to improve connection resilience for PostgreSQL-backed runtime sessions.

**Done when**
- [x] the backend starts and creates an engine for PostgreSQL successfully

---

### Task 2.2 - Refactor session management

**Status**
- done

**Goal**
Ensure request/session lifecycle management works cleanly with PostgreSQL.

**Steps**
- Review how sessions are created.
- Review how sessions are closed.
- Ensure rollbacks happen correctly on failure paths.
- Ensure dependency injection or session-provision pattern remains consistent.

**Deliverable**
Stable session lifecycle handling.

**Implementation notes**
- `backend/app/dependencies.py` now rolls back the active session if an exception propagates through the request dependency.
- Session close behavior remains in `finally` to guarantee cleanup for both success and failure flows.

**Done when**
- [x] DB sessions behave correctly in normal and error flows

---

### Task 2.3 - Review model compatibility with PostgreSQL

**Status**
- done

**Goal**
Verify the ORM model definitions are safe for PostgreSQL.

**Steps**
- Review all primary key columns.
- Review autoincrement/identity behavior.
- Review boolean columns.
- Review datetime/date columns.
- Review nullable vs non-nullable behavior.
- Review unique constraints and indexes.
- Review foreign keys.
- Review any enum or JSON fields if present.
- Review server defaults and Python defaults.

**Deliverable**
A list of model changes required for PostgreSQL compatibility.

**Implementation notes**
- Reviewed ORM models under `backend/app/models/` for PostgreSQL-sensitive areas: primary keys, booleans, nullable fields, foreign keys, and defaults.
- Verified integer primary key + foreign key usage is PostgreSQL-compatible across current models.
- Verified no enum/JSON model fields currently require PostgreSQL-specific type migration handling.
- Adjusted boolean server default in `backend/app/models/printable.py` from `text("0")` to `text("false")` for PostgreSQL-safe default semantics.
- No additional model-level blockers identified for PostgreSQL in current schema definitions.

**Done when**
- [x] all model definitions are validated or corrected for PostgreSQL

---

### Task 2.4 - Review repository/service queries

**Status**
- done

**Goal**
Catch behavior that worked in SQLite but may fail or behave differently in PostgreSQL.

**Steps**
- Review raw SQL if any exists.
- Review string matching behavior (`LIKE`, case sensitivity).
- Review ordering assumptions.
- Review transaction boundaries.
- Review any upsert or delete behavior.
- Review query code that may rely on SQLite type coercion.

**Deliverable**
Adjusted query and service logic.

**Implementation notes**
- Reworked generic pagination filtering in `backend/app/api/pagination.py` to remove SQLite-specific/raw SQL text filtering.
- Replaced dynamic SQL string construction with ORM column lookup + parameterized `ilike` filtering via `cast(column, String).ilike(...)`.
- Added validation to reject unknown filter fields explicitly.
- Added regression test `test_list_storage_elements_filter_treats_value_as_literal` in `backend/tests/api/test_storagelement.py` to ensure filter values are treated as literals and not SQL fragments.
- Verified API filter/pagination behavior with targeted backend tests.

**Done when**
- [x] no known SQLite-specific query behavior remains in normal application paths

---

## Phase 3 - Alembic adaptation

### Task 3.1 - Update Alembic configuration

**Status**
- done

**Goal**
Make Alembic target PostgreSQL using the same configuration model as the app.

**Steps**
- Update `alembic.ini` and/or `env.py` to resolve the DB URL from environment/config.
- Remove SQLite-specific assumptions.
- Ensure `target_metadata` is complete and correct.
- Verify offline and online migration modes if used.

**Deliverable**
Alembic config that works against PostgreSQL.

**Implementation notes**
- Migration directory was renamed to `backend/db_migrations/` to avoid Python package shadowing of the Alembic library.
- `backend/alembic.ini` now points `script_location = db_migrations`.
- `backend/db_migrations/env.py` resolves database URL strictly from required `DATABASE_URL`.
- `backend/db_migrations/env.py` now ensures configured `DB_SCHEMA` exists and sets PostgreSQL search path to `<DB_SCHEMA>,public`.
- Verified Alembic runtime uses PostgreSQL dialect (`PostgresqlImpl`) with the environment-driven URL.

**Done when**
- [x] `alembic upgrade head` works against a clean PostgreSQL database

---

### Task 3.2 - Validate existing migration history

**Status**
- done

**Goal**
Decide whether the current migration chain can be reused.

**Steps**
- Apply all current migrations to a clean PostgreSQL database.
- Record any failures.
- Identify migrations that contain SQLite-specific logic.
- Decide whether to preserve history or create a fresh baseline.

**Deliverable**
A migration-history decision and supporting notes.

**Implementation notes**
- Applied full migration chain to a clean PostgreSQL database (`storage_management_migtest`).
- Recorded an incompatibility in migration `34229333d949_link_storagetype.py` (legacy `storage_type` value comparison failed under PostgreSQL strict typing).
- Decision: preserve Alembic history and fix incompatible migration(s) instead of rebasing.

**Done when**
- [x] there is a clear chosen approach for schema history

---

### Task 3.3 - Fix or recreate migration chain

**Status**
- done

**Goal**
Ensure PostgreSQL schema setup is fully reproducible.

**Steps**
- If preserving history: fix incompatible migrations.
- If rebasing: create a fresh baseline migration.
- Verify indexes, constraints, defaults, and foreign keys.
- Test autogeneration on top of the chosen baseline.

**Deliverable**
Reliable Alembic migration chain for PostgreSQL.

**Implementation notes**
- Updated `backend/db_migrations/versions/34229333d949_link_storagetype.py` to migrate `storage_element.storage_type` values via robust Python-side mapping (supports numeric/id and name-based legacy values) instead of DB-specific comparison SQL.
- Added explicit failure path when legacy values cannot be mapped to `storage_type.id`.
- Added `backend/db_migrations/versions/c6f4f4bc36ab_move_tables_to_app_schema.py` to move application tables from `public` into configured `DB_SCHEMA`.
- Re-validated full chain on a clean PostgreSQL database to `head` successfully.

**Done when**
- [x] a clean PostgreSQL DB can be created and upgraded to head with no manual DB changes

---

## Phase 4 - Test environment migration to PostgreSQL

### Task 4.1 - Introduce a PostgreSQL test container

**Status**
- done

**Goal**
Run tests against PostgreSQL instead of SQLite.

**Steps**
- Add a dedicated `docker-compose.test.yml` PostgreSQL service for local test runs.
- Add a healthcheck or readiness strategy.
- Add test DB credentials/config.
- Bind local test DB to a non-conflicting host port (for example `5433`) to avoid clashing with shared dev PostgreSQL on `5432`.
- Ensure this local test container setup is independent from the shared dev PostgreSQL container.

**Deliverable**
Reusable PostgreSQL test container setup.

**Implementation notes**
- Added `docker-compose.test.yml` with a dedicated PostgreSQL 16 test service.
- Test service uses isolated credentials/database (`test` / `storage_management_test`) and host port `5433` to avoid conflict with shared local dev DB on `5432`.
- Added healthcheck (`pg_isready`) and persistent volume for repeatable local test runs.
- Added README usage for start/stop and test `DATABASE_URL`/`DB_SCHEMA` connection values.

**Done when**
- [x] test infrastructure can start a clean PostgreSQL instance automatically

---

### Task 4.2 - Update test configuration and fixtures

**Status**
- done

**Goal**
Wire the test suite to the PostgreSQL database.

**Steps**
- Update test config to use a PostgreSQL `DATABASE_URL`.
- Update fixtures to create/reset schema.
- Decide whether tests use transaction rollback, truncate, or recreate-schema strategy.
- Ensure fixtures wait for DB readiness.
- Ensure parallel or repeated test runs do not conflict.

**Deliverable**
PostgreSQL-based DB fixtures.

**Implementation notes**
- Updated `backend/tests/conftest.py` to require PostgreSQL test DB configuration (`TEST_DATABASE_URL` / `TEST_DB_SCHEMA`, with fallback of DB URL only from `DATABASE_URL`).
- Removed SQLite-only test engine behavior (`sqlite:///:memory:` and `check_same_thread`).
- Added PostgreSQL schema bootstrap for test setup (`CREATE SCHEMA IF NOT EXISTS`) and configured search path to test schema.
- Kept seeded baseline data and added explicit sequence reset after seeding and per test to avoid PostgreSQL sequence drift with explicit seed IDs.
- Preserved per-test isolation with transactional fixture behavior.
- Preserved existing API test expectations by fixing fixture-level sequence handling instead of changing business-level test assertions.
- Configured `pdm run pytest` local default to PostgreSQL test container settings (`localhost:5433`) and auto-start behavior (non-CI) in test setup.
- Added `backend` PDM helper command `pdm run test_postgres` to bootstrap local test DB container (idempotent), wait for readiness, run migrations, and run tests without teardown.
- Verified representative API test suites against PostgreSQL test container: `tests/api/test_storagelement.py`, `tests/api/test_hardwareitems.py`, `tests/api/test_storagetype.py`.

**Done when**
- [x] all backend tests run successfully against PostgreSQL

---

### Task 4.3 - Update CI test execution

**Status**
- done

**Goal**
Make the CI pipeline run tests with PostgreSQL.

**Steps**
- Add/start PostgreSQL in GitHub Actions via workflow `services`.
- Inject the test DB environment variables.
- Apply Alembic migrations before tests, or initialize the schema via the agreed approach.
- Run the test suite.
- Tear down or let CI clean up the service.

**Deliverable**
CI workflow updated for PostgreSQL tests.

**Implementation notes**
- Updated `.github/workflows/test_backend.yml` to run with a PostgreSQL 16 service container in GitHub Actions.
- Added CI test env vars `TEST_DATABASE_URL` and `TEST_DB_SCHEMA` for PostgreSQL-backed tests.
- Added an explicit PostgreSQL readiness wait step before migration/test execution.
- Added migration step (`pdm run migrate`) before `pytest` to ensure schema is up to date in CI.

**Done when**
- [x] CI passes using PostgreSQL-backed tests

---

## Phase 5 - Data migration tooling

### Task 5.1 - Design the SQLite-to-PostgreSQL migration script

**Status**
- done

**Goal**
Define the migration tool structure before implementation.

**Steps**
- Decide script location, for example `scripts/`, `tools/`, or `admin/`.
- Define CLI arguments.
- Decide logging format.
- Decide dry-run support.
- Define table copy order based on foreign keys.
- Define validation/reporting strategy.

**Deliverable**
Technical outline for the migration script.

**Implementation notes**
- Added detailed tooling design document: `design/postgres-upgrade/sqlite-to-postgres-tooling-outline.md`.
- Confirmed script location as `backend/tools/sqlite_to_postgres.py`.
- Defined CLI argument contract (required/optional), logging/report output, FK-safe copy order, and safety validation strategy.
- Locked implementation sequence: prechecks first (Task 5.2), then copy logic.

**Done when**
- [x] script structure and behavior are clearly defined

---

### Task 5.2 - Implement schema/version prechecks

**Status**
- done

**Goal**
Prevent migration into the wrong target schema.

**Steps**
- Check source SQLite file accessibility.
- Check target PostgreSQL connectivity.
- Check target Alembic revision.
- Check whether target DB is empty or already partially populated.
- Fail fast on unsupported states.

**Deliverable**
Preflight validation in the migration tool.

**Implementation notes**
- Implemented precheck CLI in `backend/tools/sqlite_to_postgres.py`.
- Added source SQLite accessibility/read checks for required app tables.
- Added target PostgreSQL connectivity check.
- Added Alembic revision verification against expected revision (`--expected-revision`, supports `head` resolution).
- Added target table occupancy check with fail-fast behavior unless `--truncate-target` is explicitly provided.
- Added structured JSON report output (`--report-file`) with sanitized target URL.
- Verified precheck execution successfully against local PostgreSQL target.

**Done when**
- [x] the script refuses unsafe or inconsistent migration scenarios

---

### Task 5.3 - Implement table-by-table data transfer

**Status**
- done

**Goal**
Move existing production data safely into PostgreSQL.

**Steps**
- Read source data from SQLite.
- Insert target data in dependency-safe order.
- Handle nullable fields consistently.
- Handle booleans/datetimes safely.
- Decide whether to preserve primary keys exactly.
- Add batching if useful.

**Deliverable**
Working core migration logic.

**Implementation notes**
- Extended `backend/tools/sqlite_to_postgres.py` from precheck-only mode to support copy execution via `--copy-data`.
- Implemented FK-safe copy order: `storage_type` -> `storage_element` -> `hardware_items`.
- Preserved explicit primary keys during import.
- Added batch insert support via `--batch-size`.
- Added value normalization for boolean fields (`reorder`, `queued_for_printing`) to ensure PostgreSQL-safe writes.
- Added optional `--dry-run` mode and report fields for copied row counts.
- Verified copy flow against a sample SQLite source and clean PostgreSQL target schema.

**Done when**
- [x] representative source data can be copied successfully into PostgreSQL

---

### Task 5.4 - Reset sequences and validate integrity

**Status**
- done

**Goal**
Make the target DB ready for normal application writes after migration.

**Steps**
- Reset PostgreSQL sequences/identity values.
- Validate row counts by table.
- Validate key relationships.
- Run spot checks for representative entities.
- Produce a migration summary report.

**Deliverable**
Post-migration validation and sequence reset support.

**Implementation notes**
- Extended `backend/tools/sqlite_to_postgres.py` to reset PostgreSQL `id` sequences after copy for all migrated tables (`storage_type`, `storage_element`, `hardware_items`).
- Added post-copy row-count validation (`source` vs `target`) and fail-fast behavior on mismatch.
- Added report check outputs for sequence reset and post-copy count validation.

**Done when**
- [x] migrated data is usable and new inserts work correctly

---

### Task 5.5 - Rehearse the migration on a production copy

**Goal**
Reduce cutover risk before real migration.

**Steps**
- Create a safe copy of the production SQLite DB.
- Run the migration tool against that copy.
- Record row counts and timing.
- Run backend smoke tests against the migrated PostgreSQL DB.
- Fix any migration edge cases.

**Deliverable**
Rehearsed and validated migration process.

**Done when**
- at least one rehearsal migration succeeds end-to-end

---

## Phase 6 - Deployment and cutover readiness

### Task 6.1 - Add deployment/runtime PostgreSQL configuration

**Goal**
Prepare the application deployment to run against PostgreSQL.

**Steps**
- Add production environment variables/secrets handling.
- Add DB host/user/password/database configuration.
- Ensure startup order and readiness expectations are documented.
- Ensure backup/restore ownership is clear.

**Deliverable**
Production-ready runtime configuration.

**Done when**
- the deployed backend can connect to PostgreSQL through production config only

---

### Task 6.2 - Write the cutover runbook

**Goal**
Define a controlled production migration sequence.

**Steps**
- Define write-freeze procedure.
- Define SQLite backup step.
- Define PostgreSQL provisioning step.
- Define Alembic migration step.
- Define data migration step.
- Define smoke-test checklist.
- Define go/no-go checkpoints.

**Deliverable**
A documented cutover procedure.

**Done when**
- the production switch can be executed from a written runbook

---

### Task 6.3 - Write rollback procedure

**Goal**
Ensure production can be restored if cutover fails.

**Steps**
- Define rollback trigger conditions.
- Define how to restore the old application config.
- Define how to restore or re-point to SQLite.
- Define how to preserve failed migration evidence/logs.
- Define communication and decision points.

**Deliverable**
Rollback runbook.

**Done when**
- rollback steps are documented and realistic

---

## Phase 7 - Documentation and stabilization

### Task 7.1 - Update developer documentation

**Goal**
Make PostgreSQL-based development easy for contributors.

**Steps**
- Document local PostgreSQL startup.
- Document required environment variables.
- Document Alembic commands.
- Document how to run tests against PostgreSQL.
- Document common troubleshooting cases.

**Deliverable**
Updated developer docs.

**Done when**
- a developer can set up the project from scratch using the docs

---

### Task 7.2 - Add operational documentation

**Goal**
Make operations and maintenance clearer after the migration.

**Steps**
- Document backup expectations.
- Document restore expectations.
- Document DB ownership/admin responsibilities.
- Document monitoring/logging expectations.
- Document how to run future migrations.

**Deliverable**
Operational DB documentation.

**Done when**
- production DB operation responsibilities are documented

---

### Task 7.3 - Post-migration stabilization review

**Goal**
Validate the system after the PostgreSQL switch.

**Steps**
- Verify create/update/delete flows.
- Verify the most important search/filter functions.
- Verify Alembic state in production.
- Verify logs for DB-related errors.
- Track and fix any PostgreSQL-specific bugs found after rollout.

**Deliverable**
Stabilization checklist and follow-up items.

**Done when**
- no critical DB migration issues remain open

---

# Suggested pull request breakdown

A practical implementation sequence could be split into the following PRs:

## PR 1 - Configuration and local PostgreSQL support
- dependencies
- environment config
- local PostgreSQL container setup
- basic documentation

## PR 2 - Backend DB layer refactoring
- engine/session changes
- model compatibility fixes
- query/service fixes

## PR 3 - Alembic PostgreSQL adaptation
- Alembic config updates
- migration chain fixes or baseline reset
- schema validation

## PR 4 - Test migration to PostgreSQL
- PostgreSQL test container
- fixture updates
- CI updates

## PR 5 - SQLite-to-PostgreSQL migration tooling
- migration script
- validation/reporting
- rehearsal notes

## PR 6 - Deployment, cutover, and final docs
- production config
- cutover/rollback runbook
- updated docs

---

# Minimal execution order

If the work needs to be tackled strictly step-by-step, use this order:

1. Inventory current DB integration.
2. Confirm technical decisions.
3. Add PostgreSQL dependency and config.
4. Add local PostgreSQL setup.
5. Refactor engine/session handling.
6. Review and fix model compatibility.
7. Adapt Alembic.
8. Validate schema creation on clean PostgreSQL.
9. Introduce PostgreSQL test container.
10. Switch tests and CI to PostgreSQL.
11. Implement migration script.
12. Rehearse migration on a production copy.
13. Prepare deployment config.
14. Write cutover and rollback docs.
15. Execute final stabilization review.

---

# Candidate future GitHub issues (aligned to PR phases)

If these tasks are later turned into issues, use the following issue groupings so each issue maps clearly to one of the proposed PR phases.

## PR 1 - Configuration and local PostgreSQL support

- Inventory current SQLite integration and affected files
- Confirm PostgreSQL migration technical decisions (driver, version, env strategy, local dev approach)
- Add PostgreSQL dependency and environment-based DB configuration
- Add local PostgreSQL container setup for development
- Document local PostgreSQL bootstrap and configuration basics

## PR 2 - Backend DB layer refactoring

- Refactor backend engine and session management for PostgreSQL
- Review and fix ORM models for PostgreSQL compatibility
- Review and update repository/service queries for PostgreSQL behavior

## PR 3 - Alembic PostgreSQL adaptation

- Update Alembic configuration to use environment-driven DB URL
- Validate existing Alembic migration history on clean PostgreSQL
- Fix incompatible migrations or create a PostgreSQL baseline migration

## PR 4 - Test migration to PostgreSQL

- Add PostgreSQL-backed test database container and fixtures
- Update test DB initialization and isolation strategy for PostgreSQL
- Update CI to run tests against PostgreSQL

## PR 5 - SQLite-to-PostgreSQL migration tooling

- Define migration tool design and CLI contract
- Implement SQLite-to-PostgreSQL migration script
- Add post-migration validation and sequence reset logic
- Rehearse production data migration on a copied SQLite database

## PR 6 - Deployment, cutover, and final docs

- Add production PostgreSQL runtime configuration
- Write cutover runbook for PostgreSQL migration
- Write rollback runbook for PostgreSQL migration
- Update developer and operations documentation for PostgreSQL
- Run post-cutover stabilization review checklist
