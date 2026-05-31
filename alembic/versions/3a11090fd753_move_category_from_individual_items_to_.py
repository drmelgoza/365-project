"""move category from individual items to individual plans

Revision ID: 3a11090fd753
Revises: 744b8aee5218
Create Date: 2026-05-31 11:18:07.749101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a11090fd753'
down_revision: Union[str, None] = '744b8aee5218'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_plans",
        sa.Column("category", sa.String(), nullable=True)
    )

    op.execute("""
        UPDATE user_plans
        SET category = sub.category
        FROM (
            SELECT DISTINCT ON (plan_id)
                plan_id,
                category
            FROM plan_items
            WHERE category IS NOT NULL
            ORDER BY plan_id, id
        ) AS sub
        WHERE sub.plan_id = user_plans.id
    """)

    op.alter_column("user_plans", "category", nullable=False)

    op.drop_column("plan_items", "category")


def downgrade() -> None:
    op.add_column(
        "plan_items",
        sa.Column("category", sa.String(), nullable=False)
    )

    op.execute("""
        UPDATE plan_items
        SET category = user_plans.category
        FROM user_plans
        WHERE plan_items.plan_id = user_plans.id
    """)

    op.drop_column("user_plans", "category")
