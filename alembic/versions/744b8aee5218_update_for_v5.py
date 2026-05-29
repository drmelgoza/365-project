"""update for v5

Revision ID: 744b8aee5218
Revises: a1b2c3d4e5f6
Create Date: 2026-05-29 12:34:57.702992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '744b8aee5218'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("log_items_item_id_fkey", "log_items", type_="foreignkey")
    op.create_foreign_key("FK_User_Items", "log_items", "user_items",  ["item_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("FK_User_Items", "log_items", type_="foreignkey")
    op.create_foreign_key("log_items_item_id_fkey", "log_items", "user_items", ["item_id"], ["id"])
    pass
