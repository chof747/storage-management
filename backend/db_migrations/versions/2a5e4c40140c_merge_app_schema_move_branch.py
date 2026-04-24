"""merge app schema move branch

Revision ID: 2a5e4c40140c
Revises: 414c025bd919, c6f4f4bc36ab
Create Date: 2026-04-10 06:38:24.579144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a5e4c40140c'
down_revision: Union[str, None] = ('414c025bd919', 'c6f4f4bc36ab')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
