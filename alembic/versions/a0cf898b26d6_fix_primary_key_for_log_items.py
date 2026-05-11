"""fix primary key for log_items

Revision ID: a0cf898b26d6
Revises: 2ba4e0b80391
Create Date: 2026-05-11 14:30:46.645546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0cf898b26d6'
down_revision: Union[str, None] = '2ba4e0b80391'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('log_items')
    op.create_table("log_items",
                    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
                    sa.Column("log_id", sa.Integer(), sa.ForeignKey("user_logs.id"), nullable=False),
                    sa.Column("item_id", sa.Integer(), sa.ForeignKey("user_items.id"), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table('log_items')
    op.create_table("log_items",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("log_id", sa.Integer(), sa.ForeignKey("user_logs.id"), nullable=False),
                    sa.Column("item_id", sa.Integer(), sa.ForeignKey("user_items.id"), nullable=False)
                    )
