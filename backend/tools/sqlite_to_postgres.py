"""Run prechecks and optional data copy from SQLite to PostgreSQL."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text


APP_TABLES = ["storage_type", "storage_element", "hardware_items"]
TABLE_COLUMNS: dict[str, list[str]] = {
    "storage_type": ["id", "name", "printing_strategy", "description"],
    "storage_element": [
        "id",
        "name",
        "location",
        "position",
        "storage_type_id",
        "description",
    ],
    "hardware_items": [
        "id",
        "hwtype",
        "label",
        "main_metric",
        "secondary_metric",
        "length",
        "reorder",
        "reorder_link",
        "detailed_description",
        "storage_element_id",
        "queued_for_printing",
    ],
}
BOOL_COLUMNS = {"hardware_items": {"reorder", "queued_for_printing"}}
SQLITE_COLUMN_ALIASES: dict[str, dict[str, list[str]]] = {
    "storage_type": {
        "printing_strategy": ["printing_strategy", "printing_strategies"],
    }
}


class MigrationError(RuntimeError):
    """Represent a recoverable migration/precheck failure."""


@dataclass
class MigrationReport:
    """Collect execution and validation details."""

    started_at: str
    finished_at: str
    source_sqlite_path: str
    target_database_url: str
    target_schema: str
    expected_revision: str
    actual_revision: str | None
    source_table_counts: dict[str, int]
    target_table_counts: dict[str, int]
    copied_table_counts: dict[str, int] = field(default_factory=dict)
    checks: dict[str, str] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments."""

    parser = argparse.ArgumentParser(
        description="SQLite to PostgreSQL migration precheck and copy tool"
    )
    parser.add_argument(
        "--source-sqlite-path",
        required=True,
        help="Path to the source SQLite database file",
    )
    parser.add_argument(
        "--target-database-url",
        required=True,
        help="Target PostgreSQL SQLAlchemy URL",
    )
    parser.add_argument(
        "--target-schema",
        default="storage_management",
        help="Target PostgreSQL schema name",
    )
    parser.add_argument(
        "--expected-revision",
        default="head",
        help="Expected Alembic revision (or 'head')",
    )
    parser.add_argument(
        "--copy-data",
        action="store_true",
        help="Run table-by-table copy after successful prechecks",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validations only and skip copy writes",
    )
    parser.add_argument(
        "--truncate-target",
        action="store_true",
        help="Allow and clear non-empty target tables before copy",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Insert batch size when copying rows",
    )
    parser.add_argument(
        "--report-file",
        default="migration-report.json",
        help="Path for writing JSON report",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def sanitize_url(url: str) -> str:
    """Return URL with password removed for reporting."""

    parsed = urlsplit(url)
    if parsed.password is None:
        return url

    auth = parsed.username or ""
    if parsed.port:
        netloc = f"{auth}:***@{parsed.hostname}:{parsed.port}"
    else:
        netloc = f"{auth}:***@{parsed.hostname}"
    return urlunsplit(
        (parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment)
    )


def assert_valid_schema_name(schema: str) -> None:
    """Validate schema against PostgreSQL identifier rules."""

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise MigrationError("target schema name is not a valid PostgreSQL identifier")


def sqlite_table_count(connection: sqlite3.Connection, table_name: str) -> int:
    """Return row count for a SQLite table."""

    query = f'SELECT COUNT(*) FROM "{table_name}"'
    return int(connection.execute(query).fetchone()[0])


def postgres_table_count(engine, schema: str, table_name: str) -> int:
    """Return row count for a PostgreSQL table."""

    statement = text(f'SELECT COUNT(*) FROM "{schema}"."{table_name}"')
    with engine.connect() as connection:
        return int(connection.execute(statement).scalar_one())


def resolve_expected_revision(base_dir: Path, expected_revision: str) -> str:
    """Resolve 'head' to concrete revision id."""

    if expected_revision != "head":
        return expected_revision

    config = Config((base_dir / "alembic.ini").as_posix())
    script_dir = ScriptDirectory.from_config(config)
    return str(script_dir.get_current_head())


def fetch_current_revision(engine, schema: str) -> str | None:
    """Fetch alembic current revision from target schema."""

    statement = text(
        f'SELECT version_num FROM "{schema}"."alembic_version" ORDER BY version_num DESC LIMIT 1'
    )
    with engine.connect() as connection:
        result = connection.execute(statement).scalar_one_or_none()
        return str(result) if result is not None else None


def fetch_sqlite_rows(
    path: Path, table_name: str, columns: list[str]
) -> list[dict[str, Any]]:
    """Fetch rows from source SQLite table."""

    conn = sqlite3.connect(path.as_posix())
    conn.row_factory = sqlite3.Row
    try:
        available_columns = {
            str(row[1])
            for row in conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        }
        alias_map = SQLITE_COLUMN_ALIASES.get(table_name, {})

        select_exprs: list[str] = []
        for column in columns:
            candidates = alias_map.get(column, [column])
            source_name = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate in available_columns
                ),
                None,
            )
            if source_name is None:
                select_exprs.append(f'NULL AS "{column}"')
            else:
                select_exprs.append(f'"{source_name}" AS "{column}"')

        query = f'SELECT {", ".join(select_exprs)} FROM "{table_name}" ORDER BY id'
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise MigrationError(
            f"failed reading sqlite table {table_name}: {exc}"
        ) from exc
    finally:
        conn.close()


def normalize_value(table_name: str, column_name: str, value: Any) -> Any:
    """Normalize row values for PostgreSQL insert compatibility."""

    if value is None:
        return None
    if table_name == "storage_type" and column_name == "printing_strategy":
        return normalize_printing_strategy(value)
    if column_name in BOOL_COLUMNS.get(table_name, set()):
        return bool(value)
    return value


def normalize_printing_strategy(value: Any) -> Any:
    """Normalize legacy printing strategy values to text/None."""

    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)

    stripped = value.strip()
    if stripped in {"", "{}", "[]", "null"}:
        return None

    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    if decoded is None:
        return None
    if isinstance(decoded, str):
        return decoded or None
    if isinstance(decoded, list):
        if decoded and isinstance(decoded[0], str):
            return decoded[0]
        return stripped
    if isinstance(decoded, dict):
        default = decoded.get("default")
        if isinstance(default, str):
            return default
        if len(decoded) == 1:
            key = next(iter(decoded.keys()))
            if isinstance(key, str):
                return key
        return stripped
    return stripped


def truncate_target_tables(connection, schema: str) -> None:
    """Truncate target tables in reverse dependency order."""

    table_refs = ", ".join(f'"{schema}"."{name}"' for name in reversed(APP_TABLES))
    connection.execute(text(f"TRUNCATE TABLE {table_refs} RESTART IDENTITY CASCADE"))


def insert_batch(
    connection, schema: str, table_name: str, rows: list[dict[str, Any]]
) -> None:
    """Insert a batch of rows preserving explicit primary keys."""

    columns = TABLE_COLUMNS[table_name]
    column_sql = ", ".join(f'"{col}"' for col in columns)
    value_sql = ", ".join(f":{col}" for col in columns)
    statement = text(
        f'INSERT INTO "{schema}"."{table_name}" ({column_sql}) VALUES ({value_sql})'
    )
    connection.execute(statement, rows)


def copy_data(args: argparse.Namespace, source_path: Path, engine) -> dict[str, int]:
    """Copy data table-by-table from SQLite to PostgreSQL."""

    copied_counts: dict[str, int] = {}
    with engine.begin() as connection:
        if args.truncate_target:
            truncate_target_tables(connection, args.target_schema)

        for table_name in APP_TABLES:
            source_rows = fetch_sqlite_rows(
                source_path, table_name, TABLE_COLUMNS[table_name]
            )
            if not source_rows:
                copied_counts[table_name] = 0
                continue

            normalized_rows = []
            for row in source_rows:
                normalized_rows.append(
                    {
                        column: normalize_value(table_name, column, row[column])
                        for column in TABLE_COLUMNS[table_name]
                    }
                )

            for i in range(0, len(normalized_rows), args.batch_size):
                batch = normalized_rows[i : i + args.batch_size]
                insert_batch(connection, args.target_schema, table_name, batch)

            copied_counts[table_name] = len(normalized_rows)
            if args.verbose:
                print(f"Copied {copied_counts[table_name]} rows into {table_name}")

    return copied_counts


def reset_postgres_sequences(connection, schema: str) -> None:
    """Reset table id sequences to max(id) after explicit PK import."""

    for table_name in APP_TABLES:
        connection.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('"{schema}"."{table_name}"', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM "{schema}"."{table_name}"
                """
            )
        )


def validate_post_copy_counts(report: MigrationReport) -> None:
    """Ensure target row counts match source after copy."""

    mismatches = []
    for table_name in APP_TABLES:
        source_count = report.source_table_counts.get(table_name, 0)
        target_count = report.target_table_counts.get(table_name, 0)
        if source_count != target_count:
            mismatches.append(
                f"{table_name}: source={source_count} target={target_count}"
            )

    if mismatches:
        raise MigrationError(
            "post-copy row count validation failed: " + "; ".join(mismatches)
        )


def precheck(args: argparse.Namespace) -> tuple[MigrationReport, Any, Path]:
    """Run all prechecks and return report with openable target engine."""

    started = datetime.now(timezone.utc)
    checks: dict[str, str] = {}
    source_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}

    assert_valid_schema_name(args.target_schema)
    checks["schema_name"] = "ok"

    if args.batch_size < 1:
        raise MigrationError("batch-size must be >= 1")
    checks["batch_size"] = "ok"

    source_path = Path(args.source_sqlite_path)
    if not source_path.exists():
        raise MigrationError(f"source sqlite file does not exist: {source_path}")
    if not source_path.is_file():
        raise MigrationError(f"source sqlite path is not a file: {source_path}")
    checks["source_file"] = "ok"

    source_conn = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
    try:
        for table_name in APP_TABLES:
            source_counts[table_name] = sqlite_table_count(source_conn, table_name)
    except sqlite3.Error as exc:
        raise MigrationError(f"failed reading source sqlite tables: {exc}") from exc
    finally:
        source_conn.close()
    checks["source_read"] = "ok"

    try:
        engine = create_engine(args.target_database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise MigrationError(f"failed connecting to target postgres: {exc}") from exc
    checks["target_connectivity"] = "ok"

    expected_revision = resolve_expected_revision(
        Path(__file__).resolve().parents[1], args.expected_revision
    )
    checks["expected_revision"] = expected_revision

    try:
        actual_revision = fetch_current_revision(engine, args.target_schema)
    except Exception as exc:
        raise MigrationError(
            f"failed reading alembic revision from {args.target_schema}.alembic_version: {exc}"
        ) from exc

    if actual_revision != expected_revision:
        raise MigrationError(
            f"alembic revision mismatch: expected {expected_revision}, found {actual_revision}"
        )
    checks["revision_match"] = "ok"

    for table_name in APP_TABLES:
        try:
            target_counts[table_name] = postgres_table_count(
                engine, args.target_schema, table_name
            )
        except Exception as exc:
            raise MigrationError(
                f"failed reading target table {args.target_schema}.{table_name}: {exc}"
            ) from exc

    non_empty = {name: count for name, count in target_counts.items() if count > 0}
    if non_empty and not args.truncate_target:
        raise MigrationError(
            "target tables are not empty; use an empty target or pass --truncate-target: "
            + ", ".join(f"{k}={v}" for k, v in non_empty.items())
        )
    checks["target_empty_or_allowed"] = "ok"

    finished = datetime.now(timezone.utc)
    report = MigrationReport(
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        source_sqlite_path=str(source_path),
        target_database_url=sanitize_url(args.target_database_url),
        target_schema=args.target_schema,
        expected_revision=expected_revision,
        actual_revision=actual_revision,
        source_table_counts=source_counts,
        target_table_counts=target_counts,
        checks=checks,
    )
    return report, engine, source_path


def refresh_target_counts(report: MigrationReport, engine, schema: str) -> None:
    """Refresh report target row counts after copy."""

    updated: dict[str, int] = {}
    for table_name in APP_TABLES:
        updated[table_name] = postgres_table_count(engine, schema, table_name)
    report.target_table_counts = updated


def write_report(report: MigrationReport, path: Path) -> None:
    """Write report as JSON."""

    path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")


def main() -> int:
    """Run CLI entrypoint."""

    args = parse_args()
    report_path = Path(args.report_file)

    try:
        report, engine, source_path = precheck(args)

        if args.dry_run:
            report.checks["copy"] = "skipped_dry_run"
            print("Prechecks passed (dry run)")
        elif args.copy_data:
            report.copied_table_counts = copy_data(args, source_path, engine)
            with engine.begin() as connection:
                reset_postgres_sequences(connection, args.target_schema)
            refresh_target_counts(report, engine, args.target_schema)
            validate_post_copy_counts(report)
            report.checks["copy"] = "ok"
            report.checks["sequence_reset"] = "ok"
            report.checks["post_copy_counts"] = "ok"
            print("Prechecks passed and data copy completed")
        else:
            report.checks["copy"] = "skipped_no_copy_flag"
            print("Prechecks passed")

        report.finished_at = datetime.now(timezone.utc).isoformat()
        write_report(report, report_path)
        print(f"Report written to {report_path}")
        return 0
    except MigrationError as exc:
        print(f"Migration precheck/copy failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
