"""move tables to application schema

Revision ID: c6f4f4bc36ab
Revises: 8646c84fc4ef
Create Date: 2026-04-01 12:00:00.000000

"""

from typing import Sequence, Union
import os
import re

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c6f4f4bc36ab"
down_revision: Union[str, None] = "8646c84fc4ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _schema_name() -> str:
    schema = os.getenv("DB_SCHEMA", "storage_management")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise RuntimeError("DB_SCHEMA must be a valid PostgreSQL identifier")
    return schema


def _move_table_if_exists(
    source_schema: str, target_schema: str, table_name: str
) -> None:
    op.execute(
        sa.text(
            f'ALTER TABLE IF EXISTS "{source_schema}"."{table_name}" '
            f'SET SCHEMA "{target_schema}"'
        )
    )


def upgrade() -> None:
    """Move application tables from public to configured schema."""
    schema = _schema_name()
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    for table_name in ["hardware_items", "storage_element", "storage_type"]:
        _move_table_if_exists("public", schema, table_name)


def downgrade() -> None:
    """Move application tables back to public schema."""
    schema = _schema_name()

    for table_name in ["hardware_items", "storage_element", "storage_type"]:
        _move_table_if_exists(schema, "public", table_name)
