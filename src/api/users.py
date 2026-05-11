from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["users"],
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
    Creates a new user profile.
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


class NewUserStats(BaseModel):
    height: float = 0
    weight: float = 0
    age: float = 0


class UpdateUserResponse(BaseModel):
    user_id: int
    status: str


@router.get("/{user_id}", response_model=User)
def get_user_stats(user_id: int):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM users
                WHERE id = :user_id
                """
            ),
            [{
                "user_id": user_id
            }]
        ).one_or_none()

        # Our current inference as to how non-existent users should be handled.
        if not result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        else:
            user = User(
                username=result.username,
                name=result.name,
                email=result.email,
                height=result.height,
                weight=result.weight,
                age=result.age
            )

            return user


# PATCH is used here to preserve the url and
# avoid an extra url tag.
# Based off of the PATCH principles at
# https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design
# Uses default value of 0 symbolizing no change in that item.
@router.patch("/{user_id}", response_model=UpdateUserResponse)
def update_user_stats(user_id: int, new_user_stats: NewUserStats):
    """
    Update a user profile with new height, weight, and/or age metrics.
    """

    with db.engine.begin() as connection:
        user_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT * 
                FROM users
                WHERE id = :user_id
                """
            ),
            [{
                "user_id": user_id
            }]
        ).one_or_none()

    # Our current inference as to how non-existent users should be handled.
    if not user_result:
        raise HTTPException(status_code=404, detail="User does not exist.")

    # Our current inference as to how invalid input should be handled.
    if new_user_stats.height < 0 or new_user_stats.weight < 0 or new_user_stats.age < 0:
        raise HTTPException(status_code=400, detail="Values must be greater than 0.")

    else:
        with db.engine.begin() as connection:
            if new_user_stats.height != 0:
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE users
                        SET height = :height 
                        WHERE id = :user_id
                        """
                    ),
                    [{
                        "height": new_user_stats.height,
                        "user_id": user_id
                    }]
                )

            if new_user_stats.weight != 0:
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE users
                        SET weight = :weight
                        WHERE id = :user_id
                        """
                    ),
                    [{
                        "weight": new_user_stats.weight,
                        "user_id": user_id,
                    }]
                )

            if new_user_stats.age != 0:
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE users
                        SET age = :age
                        WHERE id = :user_id
                        """
                    ),
                    [{
                        "age": new_user_stats.age,
                        "user_id": user_id,
                    }]
                )

        return UpdateUserResponse(user_id=user_id, status="updated")


class LogInfo(BaseModel):
    month: int
    day: int
    year: int
    time: str
    category: str

class LogCreationResponse(BaseModel):
    log_id: int

class LoggedItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

class MealLogResponse(BaseModel):
    category: str
    month: int
    day: int
    year: int
    time: str
    items: list[LoggedItem]

@router.post("/{user_id}/logs", response_model=LogCreationResponse)
def create_meal_log(user_id: int, info: LogInfo):
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

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_logs (user_id, month, day, year, time, category)
                VALUES (:user_id, :month, :day, :year, :time, :category)
                returning id
                """
            ),
            [{
                "user_id": user_id,
                "month": info.month,
                "day": info.day,
                "year": info.year,
                "time": info.time,
                "category": info.category
            }]
        ).one()

    return LogCreationResponse(log_id=result.id)

@router.get("/{user_id}/logs/{log_id}", response_model=MealLogResponse)
def get_log(user_id:int, log_id:int):
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

        info_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT category, month, day, year, time
                FROM user_logs
                WHERE user_id = :user_id
                AND id = :log_id
                """
            ),
            [{
                "user_id": user_id,
                "log_id": log_id
            }]
        ).one_or_none()

        items_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, calories, protein, carbs, fat
                FROM log_items
                JOIN user_items on user_items.id = log_items.item_id
                WHERE log_items.log_id = :log_id 
                """
            ),
            [{
                "log_id": log_id
            }]
        ).all()

        items_list = [LoggedItem(name=itm.name, calories=itm.calories, protein=itm.protein, carbs=itm.carbs, fat=itm.fat) for itm in items_result]
        if not info_result:
            raise HTTPException(status_code=404, detail="Log not found.")

        return MealLogResponse(category=info_result.category,
                               month=info_result.month,
                               day=info_result.day,
                               year=info_result.year,
                               time=str(info_result.time),
                               items=items_list)

class NewLogItems(BaseModel):
    item_ids: list[int]

class LogItemsResponse(BaseModel):
    status: str

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

    # Our current inference as to how non-existent users should be handled.
    if not user_result:
        raise HTTPException(status_code=404, detail="User does not exist.")
    else:
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
                    "fat": new_item.fat
                }]
            ).one()

    return ItemCreateResponse(user_id=user_id, item_id=item_result.id, status="created")


