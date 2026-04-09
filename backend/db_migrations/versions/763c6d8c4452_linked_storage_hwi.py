"""linked_storage_hwi

Revision ID: 763c6d8c4452
Revises: 696a331b0566
Create Date: 2025-04-15 22:03:52.531556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '763c6d8c4452'
down_revision: Union[str, None] = '696a331b0566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('hardware_items', schema=None) as batch_op:
        batch_op.drop_column('storage_element')
        batch_op.add_column(sa.Column('storage_element_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_hardware_items_storage_element',
            'storage_element',
            ['storage_element_id'],
            ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('hardware_items', schema=None) as batch_op:
        batch_op.drop_constraint('fk_hardware_items_storage_element', type_='foreignkey')
        batch_op.drop_column('storage_element_id')
        batch_op.add_column(sa.Column('storage_element', sa.String(), nullable=True), 'reorder')