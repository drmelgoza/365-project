from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from enum import Enum
from typing import List, Optional
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class User(BaseModel):
    username: str
    name: str
    email: str
    height: float
    weight: float
    age: float


class UserCreateResponse(BaseModel):
    user_id: int


@router.post("/", response_model=UserCreateResponse)
def create_user(new_user: User):
    """
    Creates a new user profile for a specific customer.
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM users
                where email = :email
                """
            ),
            [{
            "email": new_user.email
            }]
        ).one_or_none()

    if result:
        raise HTTPException(status_code=500, detail="User with this email already exists.")
    else:
        with db.engine.begin() as connection:
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


class FoodItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class ItemCreateResponse(BaseModel):
    item_id: int
    user_id: int
    status: str


#TODO: Update Schema to include a "user_items" and "food_items" table.
#This will involve renaming the "food_item" table and creating a new
#"user_items" table that will serve as the many_to_many table
#between the two object types.
@router.post("/{user_id}/items", response_model=ItemCreateResponse)
def add_food_item(user_id: int, new_item: FoodItem):
    with db.engine.begin() as connection:
        user_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 
                FROM users
                WHERE id = :user_id
                """
            ),
            [{
            "user_id": user_id,
            }]
        ).one_or_none()

    if not user_result:
        raise HTTPException(status_code=404, detail="User does not exist.")
    else:
        with db.engine.begin() as connection:
            item_result = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO food_item (user_id, name, calories, protein, carbs, fat)
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
                "fat": new_item.fat
                }]
            ).one()

    return ItemCreateResponse(user_id=user_id, item_id=item_result.id, status="created")

#TODO: Implement Meal Logging:
#This will involve creating two new tables: "user_logs" and "log_items"
#"user_logs" will relate Users to their Logs, while "log_items"
#will relate logs (by their id value) to individual items.



