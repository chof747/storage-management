# PostgreSQL Migration Plan

## Goal

Migrate the storage-management application from the current SQLite-based setup to a PostgreSQL database hosted on a dedicated database server, while keeping local development, automated tests, Alembic migrations, and production data migration maintainable and reproducible.

## Scope

This change covers:

- setup of the new PostgreSQL database system for development, test, and production-like environments
- adapting backend database management code from SQLite-specific assumptions to PostgreSQL-compatible SQLAlchemy usage
- adapting Alembic configuration and migration workflow
- changing the automated test setup to use PostgreSQL provided by a Docker container as part of the test configuration
- creating a migration utility/script to transfer existing production data from SQLite to PostgreSQL

This change does **not** primarily aim to redesign the domain model. Functional schema changes should be minimized and only be introduced where required for PostgreSQL compatibility or long-term maintainability.

## Objectives

1. Support PostgreSQL as the primary database backend.
2. Keep configuration environment-driven so the database URL can differ by environment.
3. Preserve application behavior and data semantics.
4. Ensure migrations are reproducible via Alembic.
5. Ensure tests run against PostgreSQL instead of SQLite so backend behavior matches production more closely.
6. Provide a controlled one-time or repeatable migration path for existing production data.

## Target Architecture

### Production

- Application backend connects to a dedicated PostgreSQL server using a SQLAlchemy connection URL.
- Credentials and connection parameters are supplied via environment variables or deployment secrets.
- Alembic runs against PostgreSQL for schema creation and upgrades.

### Development

- Developers can either:
  - connect to a local PostgreSQL instance, or
  - connect to a separately managed local PostgreSQL Docker/Compose setup (outside this repository).
- The application should no longer depend on SQLite-specific defaults.

### Test

- Automated tests start or connect to a dedicated PostgreSQL container.
- Test database schema is initialized through Alembic migrations or a controlled schema setup step.
- Tests should isolate state between test runs, ideally by creating a dedicated test database or resetting the schema between runs.
- Local test runs should use a test-only Compose setup (for example `docker-compose.test.yml`) and not depend on the shared local development PostgreSQL instance.
- CI test runs should use a GitHub Actions PostgreSQL `services` container for fully self-contained verification.

## Design Principles

### 1. Database URL as a first-class configuration item

The backend should centralize database configuration in one place and treat the SQLAlchemy database URL as the primary switch between environments.

For PostgreSQL schema isolation, use a dedicated schema setting (`DB_SCHEMA`) so application tables are kept outside the shared `public` schema.

Examples:

- `postgresql+psycopg://user:password@dbhost:5432/storage_management`
- `postgresql+psycopg://test:test@localhost:5432/storage_management_test`
- `DB_SCHEMA=storage_management`

The code should avoid hardcoded SQLite file paths except possibly in legacy migration utilities.

### 2. Remove SQLite-specific assumptions

SQLite often allows patterns that PostgreSQL is stricter about. The migration should identify and eliminate assumptions such as:

- implicit autoincrement behavior that depends on SQLite internals
- SQLite-specific SQL or type handling
- relying on loose typing
- schema creation shortcuts used only for local file-based databases
- tests that pass only because SQLite behaves differently from PostgreSQL

### 3. Alembic as the single source of schema evolution

All schema creation and evolution for PostgreSQL should happen via Alembic. The application runtime should avoid hidden schema creation where possible.

### 4. Production-like testing

Because the target system is PostgreSQL, tests should validate against PostgreSQL, not SQLite. This reduces the risk of production-only failures.

## Work Packages

## WP1 - Assess current database integration

### Purpose

Create a precise inventory of the current database-related implementation.

### Tasks

- Identify the current SQLAlchemy engine/session setup.
- Identify where SQLite file paths are configured.
- Identify any startup-time schema creation logic.
- Review SQLAlchemy models for SQLite-specific column definitions or defaults.
- Review Alembic `env.py`, migration scripts, and connection settings.
- Review test fixtures, test bootstrap code, and CI/test container setup.
- Review deployment/runtime configuration for current DB handling.

### Deliverable

A short implementation inventory noting exactly which files must be changed.

## WP2 - Introduce PostgreSQL infrastructure and configuration

### Purpose

Make PostgreSQL the supported runtime database.

### Tasks

- Define required PostgreSQL version and client driver.
- Add/update backend dependencies, likely including:
  - PostgreSQL driver (`psycopg` preferred)
  - any settings/configuration dependency if needed
- Define environment variables, for example:
  - `DATABASE_URL`
  - `POSTGRES_HOST`
  - `POSTGRES_PORT`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
- Decide whether the application uses a single `DATABASE_URL` or builds it from separate variables.
- Add local/dev container support, preferably via Docker Compose or equivalent.
- Document minimal external local PostgreSQL requirements and connection setup.

### Deliverable

A documented PostgreSQL configuration approach that works for development, testing, and production, including connection to an external local Docker PostgreSQL instance.

## WP3 - Adapt backend DB management code

### Purpose

Refactor backend database access so it is cleanly compatible with PostgreSQL.

### Tasks

- Update engine creation to use the configured PostgreSQL URL.
- Review engine arguments and remove SQLite-only `connect_args`.
- Review session lifecycle handling.
- Ensure transactions, commits, rollbacks, and connection cleanup are handled consistently.
- Review SQLAlchemy model definitions for compatibility, including:
  - primary keys and sequences/identity behavior
  - booleans
  - timestamps/date handling
  - text vs varchar usage where relevant
  - uniqueness and foreign key constraints
- Review any raw SQL queries for PostgreSQL compatibility.
- Review code that relies on case sensitivity, `LIKE` semantics, or ordering behavior.

### Specific attention points

- SQLite tolerates missing constraints and relaxed typing more often than PostgreSQL.
- PostgreSQL may require explicit schema migration for defaults and constraints that SQLite inferred or ignored.
- Any `JSON`/`JSONB`, date/time, or enum-related fields should be reviewed carefully.

### Deliverable

A backend that connects to PostgreSQL and runs the application successfully without SQLite-specific workarounds.

## WP4 - Adapt Alembic

### Purpose

Ensure Alembic migrations are correct and authoritative for PostgreSQL.

### Tasks

- Update Alembic configuration to read the runtime database URL from environment/configuration.
- Review `env.py` and migration context configuration.
- Validate autogeneration behavior against PostgreSQL.
- Create a clean baseline migration if needed, or continue from the current migration history if it is reliable.
- Verify all existing migrations apply successfully to an empty PostgreSQL database.
- Add guidelines for future migrations so schema updates remain database-safe.

### Decision to make

Choose one of these approaches:

#### Option A - Preserve migration history

Use the existing Alembic history and adapt only what is necessary.

**Pros:**
- Maintains historical continuity
- Less disruptive if current migrations are already correct

**Cons:**
- May carry SQLite-specific assumptions forward

#### Option B - Create a new PostgreSQL baseline

Create a fresh baseline migration representing the current production schema and archive the old SQLite-oriented history.

**Pros:**
- Cleaner start for PostgreSQL
- Easier to reason about if migration history is inconsistent

**Cons:**
- Requires careful coordination and clear cutover documentation

### Recommended direction

Prefer **Option A** if current Alembic history is complete and trustworthy. Use **Option B** only if the current history is incomplete or too SQLite-specific.

### Deliverable

Alembic migrations that can initialize and upgrade a PostgreSQL schema reliably.

## WP5 - Adapt the test setup to PostgreSQL via Docker

### Purpose

Run automated tests against PostgreSQL in a reproducible way.

### Tasks

- Add a PostgreSQL test container definition.
- Integrate the container into the test workflow.
- Expose a dedicated test database URL to the test runner.
- Update test fixtures so they:
  - wait until PostgreSQL is ready
  - create/reset schema before test execution
  - isolate test state between tests or test sessions
- Decide whether the test setup uses:
  - a dedicated `docker-compose.test.yml`, or
  - a test service integrated into the main Compose/CI setup, or
  - a Dockerfile/container helper plus CI orchestration
- Update CI to start the PostgreSQL service before running tests.

### Recommended test strategy

- Start PostgreSQL in a container.
- Apply Alembic migrations to the test database.
- Run tests.
- Tear down the container or reset the database afterwards.
- In CI, use GitHub Actions `services` for PostgreSQL.
- Locally, use a repository-managed test-only Compose service on a non-conflicting host port (for example `5433`).

### Notes

A plain Dockerfile alone is usually not enough to orchestrate test execution; in practice this often works best with Docker Compose or CI service containers. If the repository already uses a specific CI pattern, align with that instead of introducing a second mechanism.

### Deliverable

A reproducible automated test environment using PostgreSQL in a container.

## WP6 - Build a production data migration utility

### Purpose

Transfer existing production data from SQLite to PostgreSQL safely.

### Migration strategy

Use a dedicated migration script/tool that:

1. connects read-only to the current SQLite production database
2. connects write-enabled to the target PostgreSQL database
3. verifies the target schema version before import
4. migrates data table by table in dependency-safe order
5. resets PostgreSQL sequences/identity values after import
6. performs row-count and consistency checks
7. outputs a migration report/log

### Tasks

- Define the source-to-target table order based on foreign keys.
- Decide whether to use:
  - SQLAlchemy ORM-based copy logic, or
  - SQLAlchemy Core / bulk inserts, or
  - PostgreSQL `COPY`-assisted import for large tables
- Implement sequence reset logic after inserts.
- Add validation checks, such as:
  - row counts per table
  - null/required field validation
  - spot checks on key business entities
- Make the migration idempotent or clearly document it as one-time-use only.
- Add dry-run mode if feasible.
- Add logging and clear failure handling.

### Important technical points

- SQLite and PostgreSQL may differ in boolean, datetime, and autoincrement handling.
- Text values, empty strings, and nulls should be checked carefully.
- Foreign key insertion order matters.
- After importing explicit primary key values, PostgreSQL sequences must be advanced to the correct next value.

### Validation checklist

- Schema version on target matches expected Alembic revision.
- Row counts match for all migrated tables.
- Application starts and reads production data correctly from PostgreSQL.
- Sample create/update/delete operations work after migration.

### Deliverable

A documented migration script plus a cutover procedure for moving existing production data.

## WP7 - Cutover and rollback planning

### Purpose

Reduce operational risk during production migration.

### Cutover steps

1. Freeze application writes.
2. Back up the SQLite production database.
3. Provision PostgreSQL database and user.
4. Apply Alembic migrations to PostgreSQL.
5. Run the migration utility.
6. Validate row counts and smoke tests.
7. Switch application configuration to PostgreSQL.
8. Start the application.
9. Monitor logs and database behavior.

### Rollback plan

- Keep the SQLite production database backup unchanged.
- Keep the old application configuration available.
- If smoke tests fail after cutover, revert the application configuration to SQLite and restart the previous deployment.
- Only decommission SQLite after a defined stabilization period.

### Deliverable

A written cutover and rollback runbook.

## WP8 - Documentation and operations

### Purpose

Make the new setup maintainable by developers and operators.

### Tasks

- Update developer setup documentation.
- Document local PostgreSQL startup and credentials.
- Document how to run Alembic migrations.
- Document how to run tests with PostgreSQL.
- Document the production migration procedure.
- Document backup/restore expectations for PostgreSQL.
- Document monitoring requirements and operational ownership.

### Deliverable

Updated project documentation for development, testing, deployment, and migration.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hidden SQLite-specific behavior in code | Runtime failures on PostgreSQL | Review models, queries, and tests; test against PostgreSQL early |
| Incomplete or fragile Alembic history | Failed schema initialization | Validate migrations on a clean PostgreSQL DB; consider fresh baseline if necessary |
| Test setup becomes slow or flaky | Reduced CI reliability | Use a lightweight PostgreSQL service container and deterministic DB reset logic |
| Data migration misses edge cases | Production data corruption or cutover delays | Add dry-run, row-count checks, and smoke tests |
| Sequence values not reset after import | Insert failures after go-live | Explicitly reset all sequences after migration |
| Environment/configuration drift | Different behavior between dev, test, prod | Standardize around `DATABASE_URL` and documented container setup |

## Acceptance Criteria

The work is complete when all of the following are true:

- the backend runs successfully against PostgreSQL
- configuration no longer depends on SQLite-specific defaults for normal operation
- Alembic can initialize and upgrade a PostgreSQL database from scratch
- automated tests run against a PostgreSQL container
- CI/test documentation reflects the new database setup
- a migration script exists and has been validated against a copy of production data
- a cutover and rollback procedure is documented
- the application can read existing migrated data and perform new writes successfully

## Proposed Implementation Sequence

1. Inventory current DB integration.
2. Introduce PostgreSQL configuration and local container support.
3. Refactor backend DB/session management.
4. Validate and adapt Alembic.
5. Switch tests to PostgreSQL containers.
6. Implement and validate the SQLite-to-PostgreSQL migration script.
7. Write cutover/rollback documentation.
8. Perform a rehearsal migration before production cutover.

## Open Decisions

The implementation should explicitly decide the following:

- Which PostgreSQL version will be the project standard?
- Which driver will be used (`psycopg` recommended)?
- Will local development use Docker Compose, a native DB, or both?
- Will Alembic history be preserved or replaced with a PostgreSQL baseline?
- Will test isolation happen per test session, per module, or per test case?
- Will the migration tool be designed as one-time cutover tooling or as a reusable admin command?

## Recommended Defaults

Unless repository constraints indicate otherwise, the following defaults are recommended:

- PostgreSQL 16
- `psycopg` (v3)
- `DATABASE_URL` as the primary configuration entry
- Alembic-driven schema setup
- PostgreSQL test container integrated into CI
- dedicated migration script under a tooling/admin path
- rehearsal migration on a production copy before final cutover

## Suggested File-Level Outcomes

Likely repository areas affected:

- backend configuration module(s)
- SQLAlchemy engine/session setup
- model definitions where PostgreSQL compatibility needs tightening
- Alembic configuration and migration scripts
- test fixtures and test bootstrap
- CI workflow and/or test container config
- deployment configuration
- migration tooling/scripts
- developer and operations documentation

## Definition of Done

This migration is done when PostgreSQL is the supported primary database across runtime, migrations, tests, and deployment, and when an existing SQLite production dataset can be transferred with a documented and validated migration process.
