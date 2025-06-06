"""initial schema

Revision ID: ac86aef280b5
Revises:
Create Date: 2025-04-13 17:48:08.624685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ac86aef280b5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def downgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_hardware_items_id", table_name="hardware_items")
    op.drop_table("hardware_items")
    # ### end Alembic commands ###


def upgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hardware_items",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("hwtype", sa.VARCHAR(), nullable=False),
        sa.Column("main_metric", sa.VARCHAR(), nullable=False),
        sa.Column("secondary_metric", sa.VARCHAR(), nullable=True),
        sa.Column("length", sa.FLOAT(), nullable=True),
        sa.Column("location", sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hardware_items_id", "hardware_items", ["id"], unique=False)

    op.create_table(
        "storage_element",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("location", sa.VARCHAR(), nullable=False),
        sa.Column("position", sa.VARCHAR(), nullable=False),
        sa.Column("storage_type", sa.FLOAT(), nullable=False),
        sa.Column("description", sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_storage_element_id", "storage_element", ["id"], unique=False)

    # ### end Alembic commands ###
