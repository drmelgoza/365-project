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
    #Update foreign keys to perform cascading deletes

    #for log_items_table
    op.drop_constraint("log_items_item_id_fkey", "log_items", type_="foreignkey")
    op.drop_constraint("log_items_log_id_fkey", "log_items", type_="foreignkey")
    op.create_foreign_key("FK_user_items", "log_items", "user_items",  ["item_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("FK_user_logs", "log_items", "user_logs", ["log_id"], ["id"], ondelete="CASCADE")

    #for plan_items table
    op.drop_constraint("plan_items_plan_id_fkey", "plan_items", type_="foreignkey")
    op.create_foreign_key("FK_plan_items", "plan_items", "user_plans", ["plan_id"], ["id"])

    #for macro_goal table
    op.drop_constraint("macro_goal_user_id_fkey", "macro_goal", type_="foreignkey")
    op.create_foreign_key("FK_user_id", "macro_goal", "users", ["user_id"], ["id"], ondelete="CASCADE")

    #for user_items table
    op.drop_constraint("food_item_user_id_fkey", "user_items", type_="foreignkey")
    op.create_foreign_key("FK_user_id", "user_items", "users", ["user_id"], ["id"], ondelete="CASCADE")

    # for user_logs table
    op.drop_constraint("meal_log_user_id_fkey", "user_logs", type_="foreignkey")
    op.create_foreign_key("FK_user_id", "user_logs", "users", ["user_id"], ["id"], ondelete="CASCADE")

    # for user_plans table
    op.drop_constraint("meal_plan_user_id_fkey", "user_plans", type_="foreignkey")
    op.create_foreign_key("FK_user_id", "user_plans", "users", ["user_id"], ["id"], ondelete="CASCADE")

    #remove "schedule" in place of "schedule type" and "days"; keeps the two info pieces separate
    #op.drop_column("user_plans", "schedule")
    op.add_column("user_plans", sa.Column("schedule_type", sa.String(), nullable=False))
    op.add_column("user_plans", sa.Column("days", sa.ARRAY(sa.String()), nullable=False))

    #add optional quantity for meal plan items
    #unlike macros, many ways to measure portions
    #keep this field as a string to allow for user customization for portioning
    #ex: "handful" of grapes or "1 cup" of grapes or "bunch" of grapes
    op.add_column("plan_items", sa.Column("quantity_w_unit", sa.String, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("plan_items", "quantity_w_unit")

    op.drop_column("user_plans", "schedule_type")
    op.drop_column("user_plans", "days")
    op.add_column("user_plans", sa.Column("schedule", sa.String(), nullable=False))

    op.drop_constraint("FK_user_id", "user_plans", type_="foreignkey")
    op.create_foreign_key("meal_plan_user_id_fkey", "user_plans", "users", ["user_id"], ["id"])

    op.drop_constraint("FK_user_id", "user_logs", type_="foreignkey")
    op.create_foreign_key("meal_log_user_id_fkey", "user_logs", "users", ["user_id"], ["id"])

    op.drop_constraint("FK_user_id", "user_items", type_="foreignkey")
    op.create_foreign_key("food_item_user_id_fkey", "user_items", "users", ["user_id"], ["id"])

    op.drop_constraint("FK_user_id", "macro_goal", type_="foreignkey")
    op.create_foreign_key("macro_goal_user_id_fkey", "macro_goal", "users", ["user_id"], ["id"])


    op.drop_constraint("FK_plan_items", "plan_items", type_="foreignkey")
    op.create_foreign_key("plan_items_plan_id_fkey", "plan_items", "user_plans", ["plan_id"], ["id"])

    op.drop_constraint("FK_user_items", "log_items", type_="foreignkey")
    op.drop_constraint("FK_user_logs", "log_items", type_="foreignkey")
    op.create_foreign_key("log_items_item_id_fkey", "log_items", "user_items", ["item_id"], ["id"])
    op.create_foreign_key("log_items_log_id_fkey", "log_items", "user_logs", ["log_id"], ["id"])
