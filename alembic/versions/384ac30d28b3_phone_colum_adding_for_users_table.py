"""phone colum adding for users table

Revision ID: 384ac30d28b3
Revises: 
Create Date: 2026-09-01 20:23:04.770401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '384ac30d28b3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))
    # terminal command: alembic upgrade 384ac30d28b3


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number')
    # terminal command: alembic downgrade 384ac30d28b3