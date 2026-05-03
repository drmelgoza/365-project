"""build profiles for v1

Revision ID: eefb11c3bc44
Revises: e91d0c24f7d0
Create Date: 2026-05-03 13:27:33.161709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eefb11c3bc44'
down_revision: Union[str, None] = 'e91d0c24f7d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("global_inventory")

    op.create_table("user",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("username", sa.String(), nullable=False),
                    sa.Column("name", sa.String(), nullable=False),
                    sa.Column("email", sa.String(), nullable=False),
                    sa.Column("height", sa.Float(), nullable=False),
                    sa.Column("weight", sa.Float(), nullable=False),
                    sa.Column("age", sa.Float(), nullable=False))

    op.create_table("food_item",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("name", sa.String(), nullable=False),
                    sa.Column("calories", sa.Float(), nullable=False),
                    sa.Column("protein", sa.Float(), nullable=False),
                    sa.Column("carbs", sa.Float(), nullable=False),
                    sa.Column("fat", sa.Float(), nullable=False))

    op.create_table("macro_goal",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("nutrient", sa.String(), nullable=False),
                    sa.Column("quantity", sa.Integer(), nullable=False),
                    sa.Column("unit", sa.String(), nullable=False))

    op.create_table("meal_plan",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("name", sa.String(), nullable=False),
                    sa.Column("schedule", sa.String(), nullable=False))

    op.create_table("meal_log",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("category", sa.String(), nullable=False),
                    sa.Column("time", sa.TIMESTAMP, nullable=False))


def downgrade() -> None:
    op.drop_table("user")
    op.drop_table("food_item")
    op.drop_table("macro_goal")
    op.drop_table("meal_plan")
    op.drop_table("meal_log")