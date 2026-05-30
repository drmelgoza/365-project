from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset the tracker database by removing all users and user objects.
    Truncates all tables explicitly, resets serial sequences, and cascades
    to dependent tables (user_logs, log_items, user_items, meal_plan, macro_goal).
    """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                TRUNCATE users, user_items, user_logs, log_items, user_plans, user_goals, plan_items
                RESTART IDENTITY CASCADE
                """
            )
        )