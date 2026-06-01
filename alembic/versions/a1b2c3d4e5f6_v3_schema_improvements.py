"""v3 schema improvements: date column, age int, non-negative constraints

Revision ID: a1b2c3d4e5f6
Revises: 3abf19145c19
Create Date: 2026-05-22 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'a0cf898b26d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Replace split month/day/year/time columns with a single date column in user_logs
    op.drop_column('user_logs', 'month')
    op.drop_column('user_logs', 'day')
    op.drop_column('user_logs', 'year')
    op.drop_column('user_logs', 'time')

    # Existing rows will have date = NULL; new inserts always supply a date
    op.add_column(
        'user_logs',
        sa.Column('date', sa.Date(), nullable=True)
    )

    # Change age from FLOAT to INTEGER
    op.alter_column(
        'users',
        'age',
        type_=sa.Integer(),
        existing_type=sa.Float(),
        postgresql_using='age::integer'
    )

    # Add non-negative check constraints on user physical attributes
    op.create_check_constraint('ck_users_height_nonneg', 'users', 'height >= 0')
    op.create_check_constraint('ck_users_weight_nonneg', 'users', 'weight >= 0')
    op.create_check_constraint('ck_users_age_nonneg', 'users', 'age >= 0')

    # Add non-negative check constraints on food item nutrition values
    for col in ('calories', 'protein', 'carbs', 'fat'):
        op.create_check_constraint(
            f'ck_user_items_{col}_nonneg',
            'user_items',
            f'{col} >= 0'
        )


def downgrade() -> None:
    # Remove nutrition check constraints
    for col in ('calories', 'protein', 'carbs', 'fat'):
        op.drop_constraint(f'ck_user_items_{col}_nonneg', 'user_items')

    # Remove user attribute check constraints
    op.drop_constraint('ck_users_age_nonneg', 'users')
    op.drop_constraint('ck_users_weight_nonneg', 'users')
    op.drop_constraint('ck_users_height_nonneg', 'users')

    # Revert age back to float
    op.alter_column(
        'users',
        'age',
        type_=sa.Float(),
        existing_type=sa.Integer(),
    )

    # Remove date column and restore split columns
    op.drop_column('user_logs', 'date')
    op.add_column('user_logs', sa.Column('month', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('day', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('user_logs', sa.Column('time', sa.TIME(), nullable=True))
