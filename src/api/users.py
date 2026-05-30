from datetime import date
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
import sqlalchemy
from sqlalchemy import Boolean

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)


#create_user models
class User(BaseModel):
    username: str
    name: str
    email: EmailStr
    height: float = Field(ge=0)
    weight: float = Field(ge=0)
    age: int = Field(ge=0)


class UserCreateResponse(BaseModel):
    user_id: int


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

def validate_item(item_id: int) -> bool:
    with db.engine.begin() as connection:
        item_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_items
                WHERE id = :item_id
                """
            ),
            [{
                "item_id": item_id,
            }]
        ).one_or_none()

        return True if item_result else False

def validate_goal(user_id: int, goal:str) -> bool:
    with db.engine.begin() as connection:
        goal_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM macro_goal
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


@router.post("/", response_model=UserCreateResponse)
def create_user(new_user: User):
    """
    Creates a new user profile.
    """
    with db.engine.begin() as connection:
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM users
                WHERE email = :email
                """
            ),
            [{"email": new_user.email}]
        ).one_or_none()

        if existing:
            #duplicate email, return 409 not 500
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists."
            )

        new = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username, name, email, height, weight, age)
                VALUES (:username, :name, :email, :height, :weight, :age)
                RETURNING id
                """
            ),
            [{
                "username": new_user.username,
                "name": new_user.name,
                "email": new_user.email,
                "height": new_user.height,
                "weight": new_user.weight,
                "age": new_user.age,
            }]
        ).one()

    return UserCreateResponse(user_id=new.id)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        return User(
            username=result.username,
            name=result.name,
            email=result.email,
            height=result.height,
            weight=result.weight,
            age=result.age,
        )

#update_user models
class UpdateUserResponse(BaseModel):
    user_id: int
    status: str


#only updates fields that are not None
#optimal version if time permits: use pythonic sql to build one query to execute?
@router.patch("/{user_id}", response_model=UpdateUserResponse)
def update_user(
        user_id: int,
        new_weight_lbs: float = None,
        new_age: int = None,
        new_height_cm: float = None
):
    """Update height, weight, and/or age. Omit any field to leave it unchanged."""

    #validate user
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    # ensure values are either None or positive numbers
    check_weight = new_weight_lbs is None or new_weight_lbs > 0
    check_age = new_age is None or new_age > 0
    check_height = new_height_cm is None or new_height_cm > 0

    if not (check_height and check_age and check_weight):
        raise HTTPException(status_code=400, detail="Values must be greater than 0.")

    #return immediately if nothing is given
    if not (new_weight_lbs or new_height_cm or new_age):
        return UpdateUserResponse(user_id=user_id, status="no change")

    #change values
    with db.engine.begin() as connection:
        if new_height_cm and new_height_cm > 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET height = :height 
                    WHERE id = :user_id
                    """
                ),
                [{"height": new_height_cm, "user_id": user_id}]
            )

        if new_weight_lbs and new_weight_lbs > 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET weight = :weight
                    WHERE id = :user_id
                    """
                ),
                [{"weight": new_weight_lbs, "user_id": user_id}]
            )

        if new_age and new_age > 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET age = :age
                    WHERE id = :user_id
                    """
                ),
                [{"age": new_age, "user_id": user_id}]
            )

    return UpdateUserResponse(user_id=user_id, status="updated")


class UserDeleteResponse(BaseModel):
    user_id: int
    status: str


@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM users
                WHERE id = :user_id
                RETURNING 1
                """
            ),
            [{
                "user_id": user_id,
            }]
        ).one_or_none()

        status = "deleted" if result else "error; please try again."

        return UserDeleteResponse(user_id=user_id, status=status)



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
        unit = "g" if nutrient is not NutrientCategory.calories else "kcal"

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO macro_goal (user_id, nutrient, quantity, unit)
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
                FROM macro_goal
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
                DELETE FROM macro_goal
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




#food item models
class FoodItem(BaseModel):
    name: str
    #all values >= 0
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class ItemCreateResponse(BaseModel):
    item_id: int
    user_id: int
    status: str


@router.post("/{user_id}/items", response_model=ItemCreateResponse)
def add_food_item(user_id: int, new_item: FoodItem):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    if new_item.name == "":
        raise HTTPException(status_code=400, detail="Item name is required.")

    check_calories = new_item.calories > 0
    check_protein = new_item.protein > 0
    check_carbs = new_item.carbs > 0
    check_fat = new_item.fat > 0

    if not (check_calories and check_protein and check_carbs and check_fat):
        raise HTTPException(status_code=400, detail="Nutrient values must be greater than 0.")

    with db.engine.begin() as connection:
        item_result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_items (user_id, name, calories, protein, carbs, fat)
                VALUES (:user_id, :name, :calories, :protein, :carbs, :fat) 
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "name": new_item.name,
                "calories": new_item.calories,
                "protein": new_item.protein,
                "carbs": new_item.carbs,
                "fat": new_item.fat,
            }]
        ).one_or_none()

        status = "created" if item_result else "error; please try again"

    return ItemCreateResponse(user_id=user_id, item_id=item_result.id, status=status)

class GetFoodItem(BaseModel):
    id: int
    name: str
    #all values >= 0
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)

class ItemGetResponse(BaseModel):
    user_id: int
    items: list[GetFoodItem]


@router.get("/{user_id}/items", response_model=ItemGetResponse)
def get_food_items(user_id: int):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, calories, protein, carbs, fat
                FROM user_items 
                WHERE user_id = :user_id
                """
            ),
            [{
                "user_id": user_id
            }]
        ).all()

        items = []
        for row in result:
            items.append(
                GetFoodItem(id=row.id,
                            name=row.name,
                            calories=row.calories,
                            protein=row.protein,
                            carbs=row.carbs,
                            fat=row.fat)
            )

        return ItemGetResponse(user_id=user_id, items=items)

#Ensure delete uses cascade
class ItemDeleteResponse(BaseModel):
    user_id: int
    item_id: int
    status: str

@router.delete("/{user_id}/items/{item_id}", response_model=ItemDeleteResponse)
def delete_food_item(user_id: int, item_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_item = validate_item(item_id)
    if not valid_item:
        raise HTTPException(status_code=404, detail="Item does not exist.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_items 
                WHERE user_id = :user_id
                AND id = :item_id
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "item_id": item_id
            }]
        ).one_or_none()

        status = "deleted" if result else "error; please try again"

        return ItemDeleteResponse(user_id=user_id, item_id=item_id, status=status)
