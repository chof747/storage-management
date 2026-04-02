# SQLite to PostgreSQL Production Cutover How-To

This is a practical step-by-step runbook for moving production from SQLite to PostgreSQL with minimal risk.

## Assumptions

- You already have a running PostgreSQL instance.
- You know the production SQLite file path.
- Backend image includes the migration tooling (`backend/tools/sqlite_to_postgres.py`).
- You can update backend runtime env vars (`DATABASE_URL`, `DB_SCHEMA`) and restart containers.

---

## 0) Prepare target PostgreSQL (before cutover day)

- [ ] Create PostgreSQL database/user with write access.
- [ ] Decide production schema name (recommended: `storage_management`).
- [ ] Verify connection works from backend host.

Example target values:

- `DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<db>`
- `DB_SCHEMA=storage_management`

---

## 1) Rehearsal on a copy (strongly recommended)

- [ ] Copy current production SQLite DB to a safe test file.
- [ ] Run migration precheck in dry-run mode.
- [ ] Run full copy to a non-production PostgreSQL database.
- [ ] Validate API smoke flows against migrated data.

Example commands (from `backend/`):

```bash
pdm run python tools/sqlite_to_postgres.py \
  --source-sqlite-path "/path/to/sqlite-copy.db" \
  --target-database-url "postgresql+psycopg://<user>:<password>@<host>:5432/<rehearsal_db>" \
  --target-schema "storage_management" \
  --expected-revision head \
  --dry-run \
  --report-file "/tmp/pg-migration-rehearsal-precheck.json"

pdm run python tools/sqlite_to_postgres.py \
  --source-sqlite-path "/path/to/sqlite-copy.db" \
  --target-database-url "postgresql+psycopg://<user>:<password>@<host>:5432/<rehearsal_db>" \
  --target-schema "storage_management" \
  --expected-revision head \
  --copy-data \
  --report-file "/tmp/pg-migration-rehearsal-copy.json"
```

---

## 2) Production cutover checklist (exact order)

### A. Start maintenance window and freeze writes

- [ ] Announce maintenance window.
- [ ] Stop backend writes by stopping backend container.

Example:

```bash
docker compose stop backend
```

### B. Take final SQLite backup

- [ ] Create timestamped backup of production SQLite file.
- [ ] Keep backup immutable until cutover is accepted.

Example:

```bash
cp "/path/to/production.sqlite" "/path/to/backup/production-$(date +%Y%m%d-%H%M%S).sqlite"
```

### C. Prepare target PostgreSQL schema (run Alembic)

- [ ] Run Alembic against PostgreSQL target before data copy.

Example (from `backend/`):

```bash
DATABASE_URL="postgresql+psycopg://<user>:<password>@<host>:5432/<db>" \
DB_SCHEMA="storage_management" \
pdm run migrate
```

### D. Run data migration (SQLite -> PostgreSQL)

- [ ] Run precheck (non-dry-run).
- [ ] Run copy.
- [ ] Confirm report indicates success.

Example (from `backend/`):

```bash
pdm run python tools/sqlite_to_postgres.py \
  --source-sqlite-path "/path/to/production.sqlite" \
  --target-database-url "postgresql+psycopg://<user>:<password>@<host>:5432/<db>" \
  --target-schema "storage_management" \
  --expected-revision head \
  --dry-run \
  --report-file "/tmp/pg-migration-precheck.json"

pdm run python tools/sqlite_to_postgres.py \
  --source-sqlite-path "/path/to/production.sqlite" \
  --target-database-url "postgresql+psycopg://<user>:<password>@<host>:5432/<db>" \
  --target-schema "storage_management" \
  --expected-revision head \
  --copy-data \
  --report-file "/tmp/pg-migration-copy.json"
```

### E. Switch runtime config to PostgreSQL

- [ ] Update backend runtime env vars in production deploy config:
  - `DATABASE_URL=postgresql+psycopg://...`
  - `DB_SCHEMA=storage_management`
- [ ] Remove old SQLite `DATABASE_URL` values.

### F. Restart application containers

- [ ] Start backend with new env.
- [ ] Restart frontend if your deployment process requires it.

Example:

```bash
docker compose up -d --build backend frontend
```

### G. Post-cutover smoke validation

- [ ] Open app and verify list screens load.
- [ ] Create one new storage element and one new hardware item.
- [ ] Verify updates/deletes work.
- [ ] Confirm no DB errors in backend logs.

---

## 3) Rollback (if smoke tests fail)

- [ ] Stop backend.
- [ ] Revert backend env vars to SQLite (`DATABASE_URL=sqlite:...`).
- [ ] Restart backend.
- [ ] Keep PostgreSQL data for investigation (do not destroy immediately).

---

## Notes

- The migration tool now resets PostgreSQL sequences after copy, so new inserts should not collide on `id`.
- Do not commit production credentials to git; use deployment secrets/env injection.
