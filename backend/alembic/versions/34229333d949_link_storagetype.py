"""link-storagetype

Revision ID: 34229333d949
Revises: 5684dcc0cd06
Create Date: 2025-05-26 07:01:48.483307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


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

    # Migrate Values
    op.execute(
        """
        UPDATE storage_element
        SET storage_type_id = (
            SELECT id FROM storage_type WHERE storage_type.name = storage_element.storage_type
        )
    """
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
