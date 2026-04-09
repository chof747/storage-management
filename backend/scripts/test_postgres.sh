#!/usr/bin/env sh

set -eu

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
docker compose -f "$ROOT_DIR/docker-compose.test.yml" up -d

: "${TEST_DATABASE_URL:=postgresql+psycopg://test:test@localhost:5433/storage_management_test}"
: "${TEST_DB_SCHEMA:=storage_management_test}"
export TEST_DATABASE_URL TEST_DB_SCHEMA

pdm run python - <<'PY'
import os
import time
import psycopg

dsn = os.environ["TEST_DATABASE_URL"].replace("+psycopg", "")

for _ in range(30):
    try:
        with psycopg.connect(dsn):
            print("PostgreSQL test database is ready")
            break
    except Exception:
        time.sleep(1)
else:
    raise RuntimeError("PostgreSQL test database did not become ready in time")
PY

pdm run alembic upgrade head
pdm run pytest "$@"
