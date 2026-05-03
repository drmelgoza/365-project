"""update table names

Revision ID: e0b6be08e2f0
Revises: eefb11c3bc44
Create Date: 2026-05-03 14:54:14.677520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0b6be08e2f0'
down_revision: Union[str, None] = 'eefb11c3bc44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("user", "users")
    pass


def downgrade() -> None:
    op.rename_table("users", "user")
    pass
