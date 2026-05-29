from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from datetime import date
from enum import Enum



router = APIRouter(
    prefix="/logs",
    tags=["logs"],
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


def validate_log(log_id: int) -> bool:
    with db.engine.begin() as connection:
        log_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_logs
                WHERE id = :log_id
                """
            ),
            [{"log_id": log_id}]
        ).one_or_none()

        return True if log_result else False


class LoggedMealItem(BaseModel):
    name: str
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class LogStatusResponse(BaseModel):
    item_ids: list[int]
    status: str


class ItemDeleteResponse(BaseModel):
    status: str



#meal log models
#allowed meal categories
class MealCategory(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    supper = "supper"


#date in YYYY-MM-DD format, no time needed
class LogInfo(BaseModel):
    date: date
    category: MealCategory


class LogCreationResponse(BaseModel):
    log_id: int


class LoggedItem(BaseModel):
    name: str
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class MealLogResponse(BaseModel):
    category: str
    date: date
    items: list[LoggedItem]


@router.post("/{user_id}", response_model=LogCreationResponse)
def create_meal_log(user_id: int, info: LogInfo):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_logs (user_id, date, category)
                VALUES (:user_id, :date, :category)
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "date": info.date,
                "category": info.category.value,
            }]
        ).one()

    return LogCreationResponse(log_id=result.id)


@router.get("/{user_id}/{log_id}", response_model=MealLogResponse)
def get_meal_log(user_id: int, log_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    with db.engine.begin() as connection:
        info_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT category, date
                FROM user_logs
                WHERE user_id = :user_id
                AND id = :log_id
                """
            ),
            [{"user_id": user_id, "log_id": log_id}]
        ).one_or_none()

        if not info_result:
            raise HTTPException(status_code=404, detail="Log not found.")

        items_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, calories, protein, carbs, fat
                FROM log_items
                JOIN user_items ON user_items.id = log_items.item_id
                WHERE log_items.log_id = :log_id 
                """
            ),
            [{"log_id": log_id}]
        ).all()

        items_list = [
            LoggedItem(
                name=itm.name,
                calories=itm.calories,
                protein=itm.protein,
                carbs=itm.carbs,
                fat=itm.fat,
            )
            for itm in items_result
        ]

        return MealLogResponse(
            category=info_result.category,
            date=info_result.date,
            items=items_list,
        )



class NewLogItems(BaseModel):
    item_ids: list[int]

class LogUpdateResponse(BaseModel):
    status: str


@router.post("/{user_id}/{log_id}/items", response_model=LogUpdateResponse)
def add_items_to_log(user_id: int, log_id: int, items: NewLogItems):
    """Add one or more food items to an existing meal log."""
    with db.engine.begin() as connection:
        log_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 
                FROM user_logs 
                WHERE id = :log_id AND user_id = :user_id
                """
            ),
            {"log_id": log_id, "user_id": user_id}
        ).one_or_none()

        if not log_exists:
            raise HTTPException(status_code=404, detail="Log not found.")

        existing_items = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM user_items
                WHERE id = ANY(:item_ids) AND user_id = :user_id
                """
            ),
            [{
                "user_id": user_id,
                "item_ids": items.item_ids,
            }]
        ).fetchall()

        existing_item_ids = {row.id for row in existing_items}

        for item_id in items.item_ids:
            if item_id not in existing_item_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found."
                )

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO log_items (log_id, item_id) 
                    VALUES (:log_id, :item_id)
                    """
                ),
                {"log_id": log_id, "item_id": item_id}
            )

    return LogUpdateResponse(status="logged")


@router.delete("/{user_id}/{log_id}/items/{item_id}", response_model=ItemDeleteResponse)
def remove_items_from_log(user_id, log_id: int, item_id: int):
    with db.engine.begin() as connection:
        log_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_logs
                WHERE id = :log_id
                """
            ),
            [{"log_id": log_id}]
        ).one_or_none()

        if not log_result:
            raise HTTPException(status_code=404, detail="Log does not exist.")

        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM log_items
                WHERE log_id = :log_id 
                AND item_id = :item_id
                """
            ),
            [{"log_id": log_id, "item_id": item_id}]
        )

        #return 404 if the item was never in this log
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found in this log.")

    return ItemDeleteResponse(status="deleted")
