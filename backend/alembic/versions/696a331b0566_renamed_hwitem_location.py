"""renamed_hwitem_location

Revision ID: 696a331b0566
Revises: 0e4e5b0b58e8
Create Date: 2025-04-15 07:03:16.220607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '696a331b0566'
down_revision: Union[str, None] = '0e4e5b0b58e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'hardware_items',
        'location',
        new_column_name='storage_element'
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'hardware_items',
        'storage_element',
        new_column_name='location'
    )