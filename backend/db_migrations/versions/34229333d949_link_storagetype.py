"""link-storagetype

Revision ID: 34229333d949
Revises: 5684dcc0cd06
Create Date: 2025-05-26 07:01:48.483307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from numbers import Real


# revision identifiers, used by Alembic.
revision: str = "34229333d949"
down_revision: Union[str, None] = "5684dcc0cd06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new column (nullable at first)
    with op.batch_alter_table("storage_element", schema=None) as batch_op:
        batch_op.add_column(sa.Column("storage_type_id", sa.Integer(), nullable=True))

    # Migrate values from legacy storage_type field to FK ids.
    connection = op.get_bind()
    storage_types = connection.execute(
        sa.text("SELECT id, name FROM storage_type")
    ).fetchall()
    storage_type_by_id = {int(row.id): int(row.id) for row in storage_types}
    storage_type_by_name = {str(row.name): int(row.id) for row in storage_types}

    rows = connection.execute(
        sa.text("SELECT id, storage_type FROM storage_element")
    ).fetchall()

    unresolved_ids = []
    for row in rows:
        value = row.storage_type
        resolved_storage_type_id = None

        if isinstance(value, Real):
            resolved_storage_type_id = storage_type_by_id.get(int(value))
        elif value is not None:
            value_text = str(value)
            if value_text in storage_type_by_name:
                resolved_storage_type_id = storage_type_by_name[value_text]
            elif value_text.isdigit():
                resolved_storage_type_id = storage_type_by_id.get(int(value_text))

        if resolved_storage_type_id is None:
            unresolved_ids.append(row.id)
            continue

        connection.execute(
            sa.text(
                "UPDATE storage_element SET storage_type_id = :storage_type_id WHERE id = :id"
            ),
            {"storage_type_id": resolved_storage_type_id, "id": row.id},
        )

    if unresolved_ids:
        raise RuntimeError(
            "Could not map storage_element.storage_type values to storage_type.id "
            f"for rows: {unresolved_ids}"
        )

    # Now drop old column and set NOT NULL in one batch
    with op.batch_alter_table("storage_element", schema=None) as batch_op:
        batch_op.drop_column("storage_type")
        batch_op.alter_column("storage_type_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_storage_element_type", "storage_type", ["storage_type_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("storage_element", schema=None) as batch_op:
        batch_op.add_column(sa.Column("storage_type", sa.VARCHAR(), nullable=True))

    # Optionally repopulate the name using the foreign key (reverse of above)
    op.execute(
        """
       UPDATE storage_element
       SET storage_type = (
           SELECT name FROM storage_type WHERE storage_type.id = storage_element.storage_type_id
       )
    """
    )

    with op.batch_alter_table("storage_element", schema=None) as batch_op:
        batch_op.drop_constraint("fk_storage_element_type", type_="foreignkey")
        batch_op.drop_column("storage_type_id")
        batch_op.alter_column("storage_type", nullable=False)
