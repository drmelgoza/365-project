from enum import Enum
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["user macro goals"],
    dependencies=[Depends(auth.get_api_key)],
)

def validate_user(user_id: int) -> bool:
    with db.engine.begin() as connection:
        user_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        return True if user_result else False

def validate_goal(user_id: int, goal: str) -> bool:
    with db.engine.begin() as connection:
        goal_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_goals
                WHERE user_id = :user_id
                  AND nutrient = :goal
                """
            ),
            [{
                "user_id": user_id,
                "goal": goal
            }]
        ).one_or_none()

        return True if goal_result else False


# macro_goal_models
class NutrientCategory(str, Enum):
    protein = "protein"
    carbs = "carbs"
    fats = "fats"
    calories = "calories"

class GoalCreateResponse(BaseModel):
    user_id: int
    status: str


@router.post("/{user_id}/goals", response_model=GoalCreateResponse)
def add_macro_goal(user_id: int, nutrient:NutrientCategory, quantity: int = 1):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Value must be greater than 0.")

    with db.engine.begin() as connection:
        search_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_goals
                WHERE user_id = :user_id
                AND nutrient = :nutrient
                """
            ),
            [{
                "user_id": user_id,
                "nutrient": nutrient,
            }]
        ).one_or_none()

        if search_result:
            return GoalCreateResponse(user_id=user_id, status="goal already exists.")

        unit = "g" if nutrient is not NutrientCategory.calories else "kcal"

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_goals (user_id, nutrient, quantity, unit)
                VALUES (:user_id, :nutrient, :quantity, :unit)
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "nutrient": nutrient,
                "quantity": quantity,
                "unit": unit
            }]
        ).one_or_none()

        status = "created" if result else "error; please try again."

        return GoalCreateResponse(user_id=user_id, status=status)


# get_macro_goals models
class MacroGoal(BaseModel):
    nutrient: str
    quantity: int
    unit: str

class MacroGoalResponse(BaseModel):
    user_id: int
    goals: list[MacroGoal]


@router.get("/{user_id}/goals", response_model=MacroGoalResponse)
def get_macro_goals(user_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT nutrient, quantity, unit
                FROM user_goals
                WHERE user_id = :user_id
                """
            ),
            [{
                "user_id": user_id
            }]
        ).all()

        goals = []
        for row in result:
            goals.append(
                MacroGoal(nutrient=row.nutrient, quantity=row.quantity, unit=row.unit)
            )

        return MacroGoalResponse(user_id=user_id, goals=goals)


class GoalCategory(str, Enum):
    protein = "protein"
    carbs = "carbs"
    fats = "fats"
    calories = "calories"


class GoalUpdateResponse(BaseModel):
    user_id: int
    status: str


@router.patch("/{user_id}/goals/{goal}", response_model=GoalUpdateResponse)
def update_macro_goal(user_id: int, goal: GoalCategory, quantity: int = 1):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_goal = validate_goal(user_id, goal.value)
    if not valid_goal:
        raise HTTPException(status_code=400, detail="Goal does not exist.")

    with db.engine.begin() as connection:
        search_result = connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_goals
                SET quantity = :quantity
                WHERE user_id = :user_id 
                AND nutrient = :nutrient
                RETURNING 1
                """
            ),
            [{
                "user_id": user_id,
                "quantity": quantity,
                "nutrient": goal.value,
            }]
        ).one_or_none()

        status = "updated" if search_result else "error; please try again."

        return GoalUpdateResponse(user_id=user_id, status=status)



class GoalDeleteResponse(BaseModel):
    user_id: int
    goal: GoalCategory
    status: str

@router.delete("/{user_id}/goals/{goal}", response_model=GoalDeleteResponse)
def delete_goal(user_id: int, goal: GoalCategory):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_goal = validate_goal(user_id, goal.value)
    if not valid_goal:
        raise HTTPException(status_code=404, detail="Goal of this category does not exist for this user.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_goals
                WHERE user_id = :user_id
                AND nutrient = :nutrient
                RETURNING 1
                """
            ),
            [{
                "user_id": user_id,
                "nutrient": goal.value
            }]
        ).one_or_none()

        status = "deleted" if result else "error; please try again."
        return GoalDeleteResponse(user_id=user_id, goal=goal, status=status)

