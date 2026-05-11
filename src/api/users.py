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


#TODO: Update Schema to include a "user_items" and "food_items" table for Version 2.
#This will involve renaming the "food_item" table and creating a new
#"user_items" table that will serve as the many_to_many table
#between the two object types.

#TODO: Implement Meal Logging:
#This will involve creating two new tables: "user_logs" and "log_items"
#"user_logs" will relate Users to their Logs, while "log_items"
#will relate logs (by their id value) to individual items.

##DAVID"S WORK ______________________________________________________##

##I perosnally do not see a reason to add user_logs, meal_logs can just cotain all of the users logs and if we want a specific one,
## we just screach by User_id which is uqiue so we should only get the rows that contain that user. Logs have a lot of users, but the user has
## only one log, so its a one to many, no need for extra table

## Here, you might want to do a join to combine user_items and meal_log that way you can get both. Once again, I not sure what the attributes will
## end up being so whoever does it can figure out the join stuff

#Get call to get the items

class MealLogStatusResponse(BaseModel):
    status: str


class LoggedMealItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


class MealLogResponse(BaseModel):
    date: str
    time: str
    items: list[LoggedMealItem]

class MealLogUpdate(BaseModel):
    items: list[int]
    date: str
    time: str

@router.get("/{user_id}/log", response_model=MealLogResponse)
def get_all_logs(user_id):
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

        users_logs = connection.execute(
            sqlalchemy.text(
                """
                Select category, time
                Where user_id = :user_id
                """
            ),
            {
                "user_id": user_id,
            }
        ).all()

    if not users_logs:
        raise HTTPException(status_code=404, detail="No logs found.")

    # Not completely finished; joins need to be implemented
    All_logs = []
    for logs in users_logs:
        All_logs.append([logs[0], logs[1]])

    return MealLogResponse(
        date="1/1/21",  # placeholder since not stored yet
        time=str(users_logs.time),
        items=All_logs
    )


#POST call to added items,

@router.post("/{user_id}/log", response_model=MealLogStatusResponse)
def add_to_meal_log(user_id : int, category: str, time):
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

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO meal_log (user_id, category, time)
                VALUES (:user_id, :category, :time)
                """
            ),
            {
                "user_id": user_id,
                "category": category,
                "time": time
                }
        )

        ## User_items and Log_items implemitation to added. Attributes I would add:
        ## User_items: id, User_id (From user), food_id (From food_items)
        ## Log_items: id, Log_id (From meal_log), food_id (From food_items)
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_items (food)
                """
            )
        )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO log_items (food)
                """
            )
        )
    return MealLogStatusResponse(status="logged")

#delete to delete items

@router.delete("/{user_id}/log", response_model=MealLogStatusResponse)
def remove_from_meal_log(user_id : int, category: str, time, Food: FoodItem):
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

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM meal_log
                WHERE user_id = :user_id AND category = :category AND time = :time

                """
            ),
            {
                "user_id": user_id,
                "category": category,
                "time": time
                }
        )

## When user_items is deleted, related to the meal_log so that the correct row is removed from user_items that related to meal_log
## Maybe user TIME combined category, or maybe added a date column,
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_items
                """
            ),
        )
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM log_items          
                """
            ),
        )

    return MealLogStatusResponse(status="removed")

@router.patch("/{user_id}/log", response_model=MealLogStatusResponse)
def update_meal_log(user_id: int, log: MealLogUpdate):
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

        #TODO: Implement actual update logic here

    return MealLogStatusResponse(status="updated")


## END OF DAVID"S WORK__________________________________________________##


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

    #Our current inference as to how non-existent users should be handled.
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
