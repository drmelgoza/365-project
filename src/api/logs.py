from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
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
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class LogStatusResponse(BaseModel):
    item_ids: list[int]
    status: str


class ItemDeleteResponse(BaseModel):
    status: str


@router.post("/{log_id}/items", response_model=LogStatusResponse)
def add_to_log(log_id: int, items: "NewLogItems"):
    """Add one or more food items to an existing meal log."""
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

        logged_itms = []

        for item_id in items.item_ids:
            item_exists = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1 
                    FROM user_items 
                    WHERE id = :item_id
                    """
                ),
                [{"item_id": item_id}]
            ).one_or_none()

            if not item_exists:
                raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")

        for item_id in items.item_ids:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO log_items (log_id, item_id) 
                    VALUES (:log_id, :item_id)
                    """
                ),
                [{"log_id": log_id, "item_id": item_id}]
            )
            logged_itms.append(item_id)

    return LogStatusResponse(item_ids=logged_itms, status="logged")


class NewLogItems(BaseModel):
    item_ids: list[int]


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
