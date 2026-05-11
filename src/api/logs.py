from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/logs",
    tags=["logs"],
    dependencies=[Depends(auth.get_api_key)],
)

class LoggedMealItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class LogStatusResponse(BaseModel):
    item_id: int
    log_id: int
    status: str


class ItemDeleteResponse(BaseModel):
    status: str

@router.post("/{log_id}/items", response_model=LogStatusResponse)
def add_to_log(log_id: int, item_id: int):
    with db.engine.begin() as connection:
        log_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 
                FROM user_logs
                WHERE id = :log_id
                """
            ),
            [{
            "log_id": log_id,
            }]
        ).one_or_none()

        if not log_result:
         raise HTTPException(status_code=404, detail="Log does not exist.")

        ## User_items and Log_items implemitation to added. Attributes I would add:
        ## User_items: id, User_id (From user), food_id (From food_items)
        ## Log_items: id, Log_id (From meal_log), food_id (From food_items)
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO log_items (log_id, item_id)
                VALUES (:log_id, :item_id)
                RETURNING log_id, item_id
                """
            ),
            [{
                "log_id": log_id,
                "item_id": item_id
            }]
        ).one()

    return LogStatusResponse(item_id=result.item_id, log_id=result.log_id, status="logged")

#delete to delete items

@router.delete("/{log_id}/items/{item_id}", response_model=ItemDeleteResponse)
def remove_from_log(log_id: int, item_id: int):
    with db.engine.begin() as connection:
        log_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_logs
                WHERE id = :log_id
                """
            ),
            [{
                "log_id": log_id,
            }]
        ).one_or_none()

        if not log_result:
            raise HTTPException(status_code=404, detail="Log does not exist.")

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM log_items
                WHERE log_id = :log_id 
                AND item_id = :item_id
                """
            ),
            [{
                "user_id": log_id,
                "item_id": item_id
            }]
        )

    return ItemDeleteResponse(status="deleted")

