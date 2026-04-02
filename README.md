# Storage Management System

This is a web-based storage management solution to organise the hardware-items and consumables in my workshop.

## Features

**The application provides the following functionalities:**

- Keep information about the location and specification of hw items and consumables
- Keep an inventory of all the storage locations and boxes
- Enable indications for reordering and also keeps the track of ordering links
- Allows searching for items in the inventory
- Provides label printing capabilities to easily label bins and storage boxes

**The application will provide:**

- Provides functionalities to organise and check bill of materials for projects

**What the application does not provide:**

- Tracking the exact numbers of the items in the system (I simply do not need it at that level of granularity)
- Finding the physical boxes and bins in the workshop
- Keep track of Filaments for 3d printing (I use [spoolman][spoolman] for this)
- Keep detail track of electronic parts (I use [partsbox][partsbox] for this)

**For now - maybe later:**

- Integration into [spoolman][spoolman]
- Integration into [partsbox][partsbox]

[spoolman]: https://github.com/Donkie/Spoolman
[partsbox]: https://partsbox.com/

## Installation

**TODO:** write installation procedure

## Local PostgreSQL (external dev container)

For local development, this repository expects a running PostgreSQL server and does not manage that server container directly.

Minimal requirements:
- PostgreSQL major version: 16
- Reachable connection settings: host, port, database, user, password
- SQLAlchemy URL format: `postgresql+psycopg://<user>:<password>@<host>:<port>/<database>`
- Dedicated PostgreSQL schema name for this app via `DB_SCHEMA` (default: `storage_management`)

Example with a shared local dev server:
- `DATABASE_URL=postgresql+psycopg://pgdev_user:pgdev_pass@localhost:5432/postgres`
- `DB_SCHEMA=storage_management`

How to connect backend to local PostgreSQL:
1. Set `DATABASE_URL` and `DB_SCHEMA` in `backend/.env` (or export both in your shell).
2. Run backend migrations: `cd backend && pdm run migrate`.
3. Start backend: `cd backend && pdm run serve`.

The migration setup ensures the schema exists and places application tables in `DB_SCHEMA`.

Quick schema verification:
```bash
cd backend && pdm run python -c "from dotenv import load_dotenv; import os, psycopg; load_dotenv(); db=os.getenv('DATABASE_URL').replace('+psycopg',''); schema=os.getenv('DB_SCHEMA','storage_management'); conn=psycopg.connect(db); cur=conn.cursor(); cur.execute(\"select table_schema, table_name from information_schema.tables where table_schema=%s order by table_name\", (schema,)); print(cur.fetchall()); cur.close(); conn.close()"
```

## Local PostgreSQL for test runs

For self-contained local backend test runs, use the repository test container:

```bash
docker compose -f docker-compose.test.yml up -d
```

Connection settings for the test container:
- `TEST_DATABASE_URL=postgresql+psycopg://test:test@localhost:5433/storage_management_test`
- `TEST_DB_SCHEMA=storage_management_test`

Default backend test configuration:
- `TEST_DATABASE_URL=postgresql+psycopg://test:test@localhost:5433/storage_management_test`
- `TEST_DB_SCHEMA` optional; when omitted, pytest uses an isolated per-process schema

`pdm run pytest` will auto-start the local test container when not running in CI.

Run backend tests:

```bash
cd backend && pdm run pytest
```

One-command local test run (starts container if needed, keeps it running):

```bash
cd backend && pdm run test_postgres
```

You can still override connection settings when needed:

```bash
cd backend && TEST_DATABASE_URL=postgresql+psycopg://test:test@localhost:5433/storage_management_test TEST_DB_SCHEMA=storage_management_test pdm run test_postgres
```

Stop and clean test DB state:

```bash
docker compose -f docker-compose.test.yml down -v
```
