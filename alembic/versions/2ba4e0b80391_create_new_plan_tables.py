"""create_new_plan_tables

Revision ID: 2ba4e0b80391
Revises: 3abf19145c19
Create Date: 2026-05-11 13:50:46.055071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ba4e0b80391'
down_revision: Union[str, None] = '3abf19145c19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("meal_plan", "user_plans")
    op.create_table("plan_items", sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
                    sa.Column("plan_id", sa.Integer(), sa.ForeignKey("user_plans.id"), nullable=False),
                    sa.Column("item_id", sa.Integer(), sa.ForeignKey("user_items.id"), nullable=False),
                    sa.Column("category", sa.String(), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table("plan_items")
    op.rename_table("user_plans", "meal_plan")