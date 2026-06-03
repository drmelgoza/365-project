from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db
from src.api.users import validate_user, validate_item, validate_log
from datetime import date
from enum import Enum


router = APIRouter(
    prefix="/users",
    tags=["user meal logs"],
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


#meal log models
#allowed meal categories
class MealCategory(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    supper = "supper"


class LogResponse(BaseModel):
    user_id: int
    log_id: int
    status: str


@router.post("/{user_id}/logs", response_model=LogResponse)
def create_meal_log(user_id: int, category: MealCategory, log_date: date=date.today()):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    if not log_date:
        raise HTTPException(status_code=404, detail="Log must have a date.")

    if not category:
        raise HTTPException(status_code=404, detail="Category must be specified.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_logs (user_id, date, category)
                VALUES (:user_id, :date, :category)
                RETURNING id
                """
            ),
            {
                "user_id": user_id,
                "date": log_date,
                "category": category.value
            }
        ).one_or_none()

        status = "created" if result else "error; please try again."

    return LogResponse(user_id=user_id, log_id=result.id, status=status)


class LoggedItem(BaseModel):
    id: int
    name: str
    quantity: str
    calories: float = Field(ge=0)
    protein: float = Field(ge=0)
    carbs: float = Field(ge=0)
    fat: float = Field(ge=0)


class LogsByCategory(BaseModel):
    id_and_category: str
    items: list[LoggedItem]


class LogsByDay(BaseModel):
    date: date
    logs: list[LogsByCategory]


class GetLogResponse(BaseModel):
    results: list[LogsByDay]


@router.get("/{user_id}/logs", response_model=GetLogResponse)
def get_meal_logs(user_id: int, log_id: int = None, log_date:date = None, log_category:MealCategory=None):
    metadata_obj = sqlalchemy.MetaData()
    log_items = sqlalchemy.Table("log_items", metadata_obj, autoload_with=db.engine)
    user_items = sqlalchemy.Table("user_items", metadata_obj, autoload_with=db.engine)
    user_logs = sqlalchemy.Table("user_logs", metadata_obj, autoload_with=db.engine)

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    query = (
        sqlalchemy.select(
        user_items.c.id.label("item_id"),
        user_items.c.name.label("name"),
        sqlalchemy.func.concat(log_items.c.quantity, " ", log_items.c.unit).label("quantity"),
        user_logs.c.date.label("date"),
        sqlalchemy.func.concat("id ", user_logs.c.id, ": ", user_logs.c.category).label("category"),
        user_items.c.calories.label("calories"),
        user_items.c.protein.label("protein"),
        user_items.c.carbs.label("carbs"),
        user_items.c.fat.label("fat")
        )
        .join(log_items, log_items.c.item_id == user_items.c.id)
        .join(user_logs, user_logs.c.id == log_items.c.log_id)
        .order_by(user_logs.c.date.desc())
        .where(user_logs.c.user_id == user_id)
    )

    if log_id:
        query = query.where(log_items.c.log_id == log_id)

    if log_date:
        query = query.where(user_logs.c.date == log_date)

    if log_category:
        query = query.where(user_logs.c.category == log_category)

    with db.engine.begin() as connection:
        result = connection.execute(query).all()

        if not result:
            raise HTTPException(status_code=404, detail="No logs not found.")

        all_dates =[r.date for r in result]

        all_categories = [r.category for r in result]

        by_date_items = {log_date:
                             {category: [] for category in all_categories}
                         for log_date in all_dates}

        for itm in result:
            by_date_items[itm.date][itm.category].append(
                LoggedItem(
                    id=itm.item_id,
                    name=itm.name,
                    quantity=itm.quantity,
                    calories=itm.calories,
                    protein=itm.protein,
                    carbs=itm.carbs,
                    fat=itm.fat
                )
            )

        logs_list = []
        for day in by_date_items:
            logs = []
            for category in by_date_items[day]:
                if len(by_date_items[day][category]) > 0:
                    logs.append(
                        LogsByCategory(
                            id_and_category=category,
                            items = by_date_items[day][category]
                        )
                    )
            logs_list.append(
                LogsByDay(
                    date=day,
                    logs=logs)
            )



        return GetLogResponse(
            results=logs_list,
        )



class NewLogItems(BaseModel):
    item_ids: list[int]

class LogItemResponse(BaseModel):
    user_id: int
    log_id: int
    item_id: int
    status: str


@router.delete("/{user_id}/logs/{log_id}", response_model=LogResponse)
def delete_meal_log(user_id: int, log_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_log = validate_log(log_id)
    if not valid_log:
        raise HTTPException(status_code=404, detail="Log not found.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_logs
                WHERE user_id = :user_id
                AND id = :log_id
                RETURNING 1
                """
            ),
            {
                "user_id": user_id,
                "log_id": log_id
            }
        ).one_or_none()

        status = "deleted" if result else "error; please try again."

        return LogResponse(user_id=user_id, log_id=log_id, status=status)


@router.post("/{user_id}/logs/{log_id}/items", response_model=LogItemResponse)
def add_item_to_log(user_id: int, log_id: int, item_id: int, quantity: int = 1, unit: str = 'handful'):
    """Add a food item to an existing meal log."""
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_log = validate_log(log_id)
    if not valid_log:
        raise HTTPException(status_code=404, detail="Log not found.")

    valid_item = validate_item(item_id)
    if not valid_item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found.")


    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO log_items (log_id, item_id, quantity, unit)
                VALUES (:log_id, :item_id, :quantity, :unit)
                """
            ),
            {
                "log_id": log_id,
                "item_id": item_id,
                "quantity": quantity,
                "unit": unit
            }
        )

    return LogItemResponse(user_id=user_id, log_id=log_id, item_id=item_id, status="logged")


class ItemDeleteResponse(BaseModel):
    user_id: int
    log_id: int
    item_id: int
    status: str


@router.delete("/{user_id}/logs/{log_id}/items/{item_id}", response_model=LogItemResponse)
def remove_item_from_log(user_id:int, log_id: int, item_id: int):
    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_log = validate_log(log_id)
    if not valid_log:
        raise HTTPException(status_code=404, detail="Log not found.")

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM log_items
                WHERE log_id = :log_id 
                AND item_id = :item_id
                """
            ),
            {
                "log_id": log_id,
                "item_id": item_id
            }
        )

        #return 404 if the item was never in this log
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found in this log.")

    return LogItemResponse(user_id=user_id, log_id=log_id, item_id=item_id, status="deleted")
