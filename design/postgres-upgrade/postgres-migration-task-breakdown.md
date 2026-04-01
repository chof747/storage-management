# PostgreSQL Migration Task Breakdown

This document breaks the PostgreSQL migration into concrete implementation tasks for the `storage-management` repository.

It is intended as a practical execution plan that can later be converted into GitHub issues, milestones, or pull requests.

---

## Phase 0 - Preparation and baseline review

### Task 0.1 - Inventory the current database integration

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
- all DB-relevant files are identified
- SQLite-specific assumptions are documented

---

### Task 0.2 - Confirm technical decisions

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
- no open design blockers remain for implementation

---

## Phase 1 - Configuration and dependency setup

### Task 1.1 - Add PostgreSQL dependencies to the backend

**Goal**
Ensure the backend can connect to PostgreSQL.

**Steps**
- Add `psycopg` dependency.
- Verify SQLAlchemy dependency version is PostgreSQL-compatible.
- Verify Alembic dependency version is appropriate.
- Update lockfile/package management files if present.

**Deliverable**
Updated dependency configuration.

**Done when**
- backend environment installs successfully with PostgreSQL support

---

### Task 1.2 - Introduce DB environment configuration

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

**Done when**
- application startup can resolve the DB connection from config without relying on SQLite path defaults

---

### Task 1.3 - Add local PostgreSQL development setup

**Goal**
Make local PostgreSQL startup easy and repeatable.

**Steps**
- Add a Docker Compose service or equivalent for PostgreSQL.
- Define database name, user, password, and port.
- Add persistent volume configuration if useful for local dev.
- Add optional healthcheck.
- Document how to start and stop the DB locally.

**Deliverable**
Local PostgreSQL startup configuration.

**Done when**
- a developer can start PostgreSQL locally with one command or a short documented sequence

---

## Phase 2 - Backend database layer refactoring

### Task 2.1 - Refactor engine creation

**Goal**
Switch engine creation from SQLite assumptions to PostgreSQL-ready configuration.

**Steps**
- Update the SQLAlchemy `create_engine` call to use `DATABASE_URL`.
- Remove SQLite-only `connect_args`.
- Review pool settings if currently absent or SQLite-specific.
- Ensure the engine is created in a clean, reusable module.

**Deliverable**
PostgreSQL-ready engine configuration.

**Done when**
- the backend starts and creates an engine for PostgreSQL successfully

---

### Task 2.2 - Refactor session management

**Goal**
Ensure request/session lifecycle management works cleanly with PostgreSQL.

**Steps**
- Review how sessions are created.
- Review how sessions are closed.
- Ensure rollbacks happen correctly on failure paths.
- Ensure dependency injection or session-provision pattern remains consistent.

**Deliverable**
Stable session lifecycle handling.

**Done when**
- DB sessions behave correctly in normal and error flows

---

### Task 2.3 - Review model compatibility with PostgreSQL

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

**Done when**
- all model definitions are validated or corrected for PostgreSQL

---

### Task 2.4 - Review repository/service queries

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

**Done when**
- no known SQLite-specific query behavior remains in normal application paths

---

## Phase 3 - Alembic adaptation

### Task 3.1 - Update Alembic configuration

**Goal**
Make Alembic target PostgreSQL using the same configuration model as the app.

**Steps**
- Update `alembic.ini` and/or `env.py` to resolve the DB URL from environment/config.
- Remove SQLite-specific assumptions.
- Ensure `target_metadata` is complete and correct.
- Verify offline and online migration modes if used.

**Deliverable**
Alembic config that works against PostgreSQL.

**Done when**
- `alembic upgrade head` works against a clean PostgreSQL database

---

### Task 3.2 - Validate existing migration history

**Goal**
Decide whether the current migration chain can be reused.

**Steps**
- Apply all current migrations to a clean PostgreSQL database.
- Record any failures.
- Identify migrations that contain SQLite-specific logic.
- Decide whether to preserve history or create a fresh baseline.

**Deliverable**
A migration-history decision and supporting notes.

**Done when**
- there is a clear chosen approach for schema history

---

### Task 3.3 - Fix or recreate migration chain

**Goal**
Ensure PostgreSQL schema setup is fully reproducible.

**Steps**
- If preserving history: fix incompatible migrations.
- If rebasing: create a fresh baseline migration.
- Verify indexes, constraints, defaults, and foreign keys.
- Test autogeneration on top of the chosen baseline.

**Deliverable**
Reliable Alembic migration chain for PostgreSQL.

**Done when**
- a clean PostgreSQL DB can be created and upgraded to head with no manual DB changes

---

## Phase 4 - Test environment migration to PostgreSQL

### Task 4.1 - Introduce a PostgreSQL test container

**Goal**
Run tests against PostgreSQL instead of SQLite.

**Steps**
- Add a PostgreSQL container definition for tests.
- Add a healthcheck or readiness strategy.
- Add test DB credentials/config.
- Ensure the container can be used locally and in CI.

**Deliverable**
Reusable PostgreSQL test container setup.

**Done when**
- test infrastructure can start a clean PostgreSQL instance automatically

---

### Task 4.2 - Update test configuration and fixtures

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

**Done when**
- all backend tests run successfully against PostgreSQL

---

### Task 4.3 - Update CI test execution

**Goal**
Make the CI pipeline run tests with PostgreSQL.

**Steps**
- Add/start the PostgreSQL service in CI.
- Inject the test DB environment variables.
- Apply Alembic migrations before tests, or initialize the schema via the agreed approach.
- Run the test suite.
- Tear down or let CI clean up the service.

**Deliverable**
CI workflow updated for PostgreSQL tests.

**Done when**
- CI passes using PostgreSQL-backed tests

---

## Phase 5 - Data migration tooling

### Task 5.1 - Design the SQLite-to-PostgreSQL migration script

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

**Done when**
- script structure and behavior are clearly defined

---

### Task 5.2 - Implement schema/version prechecks

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

**Done when**
- the script refuses unsafe or inconsistent migration scenarios

---

### Task 5.3 - Implement table-by-table data transfer

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

**Done when**
- representative source data can be copied successfully into PostgreSQL

---

### Task 5.4 - Reset sequences and validate integrity

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

**Done when**
- migrated data is usable and new inserts work correctly

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

# Candidate future GitHub issues

If these tasks are later turned into issues, the following issue titles would work well:

- Inventory current SQLite integration and affected files
- Add PostgreSQL dependency and environment-based DB configuration
- Add local PostgreSQL container setup for development
- Refactor backend engine and session management for PostgreSQL
- Review and fix ORM models for PostgreSQL compatibility
- Validate and adapt Alembic migrations for PostgreSQL
- Add PostgreSQL-backed test database container and fixtures
- Update CI to run tests against PostgreSQL
- Implement SQLite-to-PostgreSQL migration script
- Add post-migration validation and sequence reset logic
- Rehearse production data migration on a copied SQLite database
- Add production PostgreSQL runtime configuration
- Write cutover and rollback runbook for PostgreSQL migration
- Update developer and operations documentation for PostgreSQL
