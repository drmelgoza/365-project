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