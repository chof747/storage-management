"""merge printing strategies and hwitem label

Revision ID: 414c025bd919
Revises: 7e006e64546c, 8646c84fc4ef
Create Date: 2025-11-21 07:54:15.182888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '414c025bd919'
down_revision: Union[str, None] = ('7e006e64546c', '8646c84fc4ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
