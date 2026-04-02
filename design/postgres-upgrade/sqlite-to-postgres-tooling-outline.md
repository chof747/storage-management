# SQLite to PostgreSQL Tooling Outline

Date: 2026-04-01
Phase: 5.1 (design only)

## Goal

Define a concrete, safe structure for a one-time/repeatable migration tool that copies production data from SQLite to PostgreSQL.

## Script location

- Primary entrypoint: `backend/tools/sqlite_to_postgres.py`
- Optional helpers (if needed during implementation):
  - `backend/tools/migration_io.py`
  - `backend/tools/migration_validate.py`
  - `backend/tools/migration_report.py`

## CLI contract

Required arguments:
- `--source-sqlite-path`: path to source SQLite file
- `--target-database-url`: PostgreSQL SQLAlchemy URL
- `--target-schema`: PostgreSQL schema name (default `storage_management`)

Optional arguments:
- `--expected-revision`: expected Alembic revision (default `head` resolution)
- `--dry-run`: validate and plan without writing target data
- `--truncate-target`: clear target tables before copy (explicit opt-in)
- `--batch-size`: insert batch size for larger tables (default `500`)
- `--report-file`: write JSON migration report (default `./migration-report.json`)
- `--verbose`: enable detailed logs

## Logging and reporting

Console log levels:
- `INFO`: stage boundaries and summary
- `WARNING`: non-fatal anomalies
- `ERROR`: fail-fast conditions

Structured report fields:
- source DB path, target DB URL (sanitized), target schema
- started/finished timestamps and total duration
- expected/found Alembic revision
- per-table row counts (source vs target)
- sequence reset actions
- validation results and failure details

## Table copy order

Use FK-safe copy order:
1. `storage_type`
2. `storage_element`
3. `hardware_items`

Notes:
- preserve primary keys during import
- after copy, reset PostgreSQL sequences to `max(id)` for each table

## Safety and validation strategy

Preflight checks:
- source SQLite file exists and is readable
- target PostgreSQL connection succeeds
- target schema exists (or can be created)
- target Alembic revision equals expected revision
- target tables are empty unless `--truncate-target` was provided

Post-copy validation:
- row counts per table match source
- representative FK integrity checks pass
- simple read/write smoke check can run after import

Failure behavior:
- fail fast on preflight mismatch
- on copy/validation failure, return non-zero exit and keep detailed report

## Implementation decision for next task

- Implement prechecks first (Task 5.2) without table copy logic.
- Add copy logic only after prechecks and report output are stable.
