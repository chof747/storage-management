"""add printing_strategies map to storage_type

Revision ID: 7e006e64546c
Revises: b049b2c878ef
Create Date: 2025-06-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e006e64546c"
down_revision: Union[str, None] = "b049b2c878ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("storage_type", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("printing_strategies", sa.JSON(), nullable=True)
        )

    storage_type = sa.table(
        "storage_type",
        sa.column("id", sa.Integer),
        sa.column("printing_strategy", sa.String),
        sa.column("printing_strategies", sa.JSON),
    )

    conn = op.get_bind()
    results = conn.execute(
        sa.select(storage_type.c.id, storage_type.c.printing_strategy)
    ).fetchall()

    for row in results:
        strategies = {}
        if row.printing_strategy:
            strategies["hwitems"] = row.printing_strategy
        conn.execute(
            storage_type.update()
            .where(storage_type.c.id == row.id)
            .values(printing_strategies=strategies)
        )

    with op.batch_alter_table("storage_type", schema=None) as batch_op:
        batch_op.alter_column(
            "printing_strategies",
            existing_type=sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        )
        batch_op.drop_column("printing_strategy")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("storage_type", schema=None) as batch_op:
        batch_op.add_column(sa.Column("printing_strategy", sa.String(), nullable=True))

    storage_type = sa.table(
        "storage_type",
        sa.column("id", sa.Integer),
        sa.column("printing_strategy", sa.String),
        sa.column("printing_strategies", sa.JSON),
    )

    conn = op.get_bind()
    results = conn.execute(
        sa.select(storage_type.c.id, storage_type.c.printing_strategies)
    ).fetchall()

    for row in results:
        strategies = row.printing_strategies or {}
        conn.execute(
            storage_type.update()
            .where(storage_type.c.id == row.id)
            .values(printing_strategy=strategies.get("hwitems"))
        )

    with op.batch_alter_table("storage_type", schema=None) as batch_op:
        batch_op.drop_column("printing_strategies")
