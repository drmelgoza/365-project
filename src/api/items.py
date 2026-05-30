from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/users",
    tags=["user food items"],
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

class ItemPatchResponse(BaseModel):
    user_id: int
    item_id: int
    status: str


@router.patch("/{user_id}/items/{item_id}", response_model=ItemPatchResponse)
def update_food_item(
    user_id: int,
    item_id: int,
    new_name: str = None,
    new_calories: float = None,
    new_protein: float = None,
    new_carbs: float = None,
    new_fat: float = None,
):

    valid_user = validate_user(user_id)
    if not valid_user:
        raise HTTPException(status_code=404, detail="User does not exist.")

    valid_item = validate_item(item_id)
    if not valid_item:
        raise HTTPException(status_code=404, detail="Item does not exist.")

    if not (new_name and new_calories and new_protein and new_carbs and new_fat):
        return ItemPatchResponse(user_id=user_id, item_id=item_id, status="no change")

    metadata = sqlalchemy.MetaData()
    user_items = sqlalchemy.Table("user_items", metadata, autoload_with=db.engine)

    query = (
        sqlalchemy.update(user_items)
        .where(user_items.c.id == item_id)
        .where(user_items.c.user_id == user_id)
    )

    if new_name:
        query = query.values(name=new_name)

    if new_calories:
        query = query.values(calories=new_calories)

    if new_protein:
        query = query.values(protein=new_protein)

    if new_carbs:
        query = query.values(carbs=new_carbs)

    if new_fat:
        query = query.values(fat=new_fat)

    with db.engine.begin() as connection:
        result = connection.execute(query.returning(1)).one_or_none()

        status = "updated" if result else "error; please try again"

    return ItemPatchResponse(user_id=user_id, item_id=item_id, status=status)

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
