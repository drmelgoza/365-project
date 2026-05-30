from datetime import date
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
import sqlalchemy
from sqlalchemy import Boolean
import re

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

class WeightUnits(str, Enum):
    kg = "kg"
    lbs = "lbs"

class HeightUnits(str, Enum):
    cm = "cm"
    ft = "ft/in"

#create_user models
class User(BaseModel):
    username: str
    name: str
    email: EmailStr
    height: str
    height_unit: str
    weight: float = Field(ge=0)
    weight_unit: str
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


@router.post("/", response_model=UserCreateResponse)
def create_user(
    username: str,
    name: str,
    email: EmailStr,
    height: str,
    height_unit: HeightUnits,
    weight: float,
    weight_unit: WeightUnits,
    age: int
):
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
            [{"email": email}]
        ).one_or_none()

        if existing:
            #duplicate email, return 409 not 500
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists."
            )

        height = height.strip()

        if height_unit == "ft/in":
            format_match = re.search(r"^[0-9]+\'[0-9]+\"$", height)
            if not format_match and not height.isnumeric():
                raise HTTPException(status_code=400, detail='''Invalid height. Please enter a number or inch height in format [x'y"].''')
            elif not format_match:
                numeric_height = int(height)
            else:
                feet, inches = height.split("'")
                inches = int(inches.replace('"', ""))
                feet = int(feet)
                numeric_height = inches + (feet * 12)

        elif height_unit == "cm":
            if not height.isnumeric():
                raise HTTPException(status_code=400, detail="Invalid height. Please enter a number.")
            else:
                numeric_height = int(height)

        new = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username, name, email, height, height_unit, weight, weight_unit, age)
                VALUES (:username, :name, :email, :height, :height_unit, :weight, :weight_unit, :age)
                RETURNING id
                """
            ),
            [{
                "username": username,
                "name": name,
                "email": email,
                "height": numeric_height,
                "height_unit": height_unit,
                "weight": weight,
                "weight_unit": weight_unit,
                "age": age,
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

        if result.height_unit == "ft/in":
            feet = int(result.height // 12)
            inches = int(result.height % 12)
            final_height = f"{feet}'{inches}"
        else:
            final_height = str(result.height)


        return User(
            username=result.username,
            name=result.name,
            email=result.email,
            height=final_height,
            height_unit=result.height_unit,
            weight=result.weight,
            weight_unit=result.weight_unit,
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
        new_weight: float = None,
        new_age: int = None,
        new_height: float = None
):

    """Update height, weight, and/or age. Omit any field to leave it unchanged."""

    #validate user
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    # ensure values are either None or positive numbers
    check_weight = new_weight is None or new_weight > 0
    check_age = new_age is None or new_age > 0
    check_height = new_height is None or new_height > 0

    if not (check_height and check_age and check_weight):
        raise HTTPException(status_code=400, detail="Values must be greater than 0.")

    #return immediately if nothing is given
    if not (new_weight or new_height or new_age):
        return UpdateUserResponse(user_id=user_id, status="no change")

    #change values
    with db.engine.begin() as connection:
        if new_height and new_height > 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET height = :height 
                    WHERE id = :user_id
                    """
                ),
                [{"height": new_height, "user_id": user_id}]
            )

        if new_weight and new_weight > 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET weight = :weight
                    WHERE id = :user_id
                    """
                ),
                [{"weight": new_weight, "user_id": user_id}]
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