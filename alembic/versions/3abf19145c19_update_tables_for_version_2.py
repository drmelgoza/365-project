"""update tables for version 2

Revision ID: 3abf19145c19
Revises: e0b6be08e2f0
Create Date: 2026-05-10 21:19:48.673098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3abf19145c19'
down_revision: Union[str, None] = 'e0b6be08e2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('food_item', 'food_items')
    op.rename_table('meal_log', 'user_logs')

    op.drop_column('user_logs', 'time')
    op.add_column('user_logs', sa.Column('month', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('day', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('time', sa.TIME(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('user_logs', 'month')
    op.drop_column('user_logs', 'day')
    op.drop_column('user_logs', 'year')
    op.drop_column('user_logs', 'time')
    op.add_column('user_logs', sa.Column('time', sa.TIMESTAMP(), nullable=True))

    op.rename_table('food_items', 'food_item')
    op.rename_table('user_logs', 'meal_log')

    pass
