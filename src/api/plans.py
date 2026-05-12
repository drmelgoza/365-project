from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    dependencies=[Depends(auth.get_api_key)],
)

# input and output response models for adding an item to meal plan
class MealPlanCreate(BaseModel):
    name: str
    schedule: str

class MealPlanCreateResponse(BaseModel):
    plan_id: int
    user_id: int
    status: str

class MealPlanAdd(BaseModel):
    item_id: int
    category: str


class MealPlanAddResponse(BaseModel):
    plan_id: int
    item_id: int
    user_id: int
    status: str

class UserPlanItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


class UserPlansLogResponse(BaseModel):
    day: str
    time: str
    category: str
    items: list[UserPlanItem]

class UserPlansCategoryLogResponse(BaseModel):
    category: str
    schedule: str
    items: list[UserPlanItem]

class UserPlansDayResponse(BaseModel):
    plan_name: str
    schedule: str
    items: list[UserPlanItem]

class UserPlansRemoveItemResponse(BaseModel):
    item_id: int
    status: str

class UserPlansRemovePlanResponse(BaseModel):
    plan_id: int
    status: str

@router.post("/{user_id}/plan", response_model=MealPlanCreateResponse)
def create_meal_plan(user_id: int, new_plan: MealPlanCreate):
    with db.engine.begin() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        plan_result = conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_plans (user_id, name, schedule)
                VALUES (:user_id, :name, :schedule)
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "name": new_plan.name,
                "schedule": new_plan.schedule
            }]
        ).one()

    return MealPlanCreateResponse(
        plan_id=plan_result.id,
        user_id=user_id,
        status="created"
    )

@router.post("/{user_id}/plan/{plan_id}/items", response_model=MealPlanAddResponse)
def add_meal_to_plan(user_id: int, plan_id: int, new_item: MealPlanAdd):
    with db.engine.begin() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        plan_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_plans
                WHERE id = :plan_id AND user_id = :user_id
                """
            ),
            [{
                "plan_id": plan_id,
                "user_id": user_id
            }]
        ).one_or_none()

        if not plan_result:
            raise HTTPException(status_code=404, detail="Plan does not exist for this user.")

        item_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_items
                WHERE id = :item_id AND user_id = :user_id
                """
            ),
            [{
                "item_id": new_item.item_id,
                "user_id": user_id
            }]
        ).one_or_none()

        if not item_result:
            raise HTTPException(status_code=404, detail="Item does not exist for this user.")

        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO plan_items (plan_id, item_id, category)
                VALUES (:plan_id, :item_id, :category)
                """
            ),
            [{
                "plan_id": plan_id,
                "item_id": new_item.item_id,
                "category": new_item.category
            }]
        )

    return MealPlanAddResponse(
        plan_id=plan_id,
        item_id=new_item.item_id,
        user_id=user_id,
        status="items added"
    )

@router.get("/{user_id}/plan", response_model=UserPlansLogResponse)
def get_meal_plan(user_id: int):
    with db.engine.connect() as conn:
        # Check user exists
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        # Check plan exists (even if empty)
        plan_exists = conn.execute(
            sqlalchemy.text(
                """
                SELECT name, schedule
                FROM user_plans
                WHERE user_id = :user_id
                LIMIT 1
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not plan_exists:
            raise HTTPException(status_code=404, detail="User plan does not exist.")

        # Get items (may be empty)
        results = conn.execute(
            sqlalchemy.text(
                """
                SELECT
                    pi.category,
                    ui.name,
                    ui.calories,
                    ui.protein,
                    ui.carbs,
                    ui.fat
                FROM plan_items pi
                JOIN user_plans up ON pi.plan_id = up.id
                JOIN user_items ui ON pi.item_id = ui.id
                WHERE up.user_id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).all()

    items = []

    for r in results:
        items.append(
            UserPlanItem(
                name=r.name,
                calories=r.calories,
                protein=r.protein,
                carbs=r.carbs,
                fat=r.fat
            )
        )

    # Use plan info even if no items
    return UserPlansLogResponse(
        day=plan_exists.name,
        time=str(plan_exists.schedule),
        category=results[0].category if results else "None",
        items=items
    )

@router.get("/{user_id}/plan/category", response_model=UserPlansCategoryLogResponse)
def get_meal_plan_by_category(user_id: int, category: str):
    with db.engine.connect() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        results = conn.execute(
            sqlalchemy.text(
                """
                SELECT
                    up.schedule,
                    pi.category,
                    ui.name,
                    ui.calories,
                    ui.protein,
                    ui.carbs,
                    ui.fat
                FROM plan_items pi
                JOIN user_plans up ON pi.plan_id = up.id
                JOIN user_items ui ON pi.item_id = ui.id
                WHERE up.user_id = :user_id
                AND pi.category = :category
                """
            ),
            [{
                "user_id": user_id,
                "category": category
            }]
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="No plans found for this category.")

    items = []

    for r in results:
        items.append(
            UserPlanItem(
                name=r.name,
                calories=r.calories,
                protein=r.protein,
                carbs=r.carbs,
                fat=r.fat
            )
        )

    first = results[0]

    return UserPlansCategoryLogResponse(
        category=first.category,
        schedule=str(first.schedule),
        items=items
    )

@router.get("/{user_id}/plan/day", response_model=UserPlansDayResponse)
def get_meal_plan_by_day(user_id: int, plan_name: str):
    with db.engine.connect() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        results = conn.execute(
            sqlalchemy.text(
                """
                SELECT
                    up.name AS plan_name,
                    up.schedule,
                    ui.name,
                    ui.calories,
                    ui.protein,
                    ui.carbs,
                    ui.fat
                FROM plan_items pi
                JOIN user_plans up ON pi.plan_id = up.id
                JOIN user_items ui ON pi.item_id = ui.id
                WHERE up.user_id = :user_id
                AND up.name = :plan_name
                """
            ),
            [{
                "user_id": user_id,
                "plan_name": plan_name
            }]
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="No plans found with this name.")

    items = []

    for r in results:
        items.append(
            UserPlanItem(
                name=r.name,
                calories=r.calories,
                protein=r.protein,
                carbs=r.carbs,
                fat=r.fat
            )
        )

    first = results[0]

    return UserPlansDayResponse(
        plan_name=first.plan_name,
        schedule=str(first.schedule),
        items=items
    )

@router.delete("/{user_id}/plan/items/{item_id}", response_model=UserPlansRemoveItemResponse)
def remove_item_from_plan(user_id: int, item_id: int):
    with db.engine.begin() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        item_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM plan_items pi
                JOIN user_plans up ON pi.plan_id = up.id
                WHERE up.user_id = :user_id
                AND pi.item_id = :item_id
                """
            ),
            [{
                "user_id": user_id,
                "item_id": item_id
            }]
        ).one_or_none()

        if not item_result:
            raise HTTPException(status_code=404, detail="Item does not exist in this user's plan.")

        conn.execute(
            sqlalchemy.text(
                """
                DELETE FROM plan_items
                USING user_plans
                WHERE plan_items.plan_id = user_plans.id
                AND user_plans.user_id = :user_id
                AND plan_items.item_id = :item_id
                """
            ),
            [{
                "user_id": user_id,
                "item_id": item_id
            }]
        )

    return UserPlansRemoveItemResponse(
        item_id=item_id,
        status="removed"
    )

@router.delete("/{user_id}/plan/{plan_id}", response_model=UserPlansRemovePlanResponse)
def remove_plan(user_id: int, plan_id: int):
    with db.engine.begin() as conn:
        user_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM users
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        plan_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM user_plans
                WHERE id = :plan_id AND user_id = :user_id
                """
            ),
            [{
                "plan_id": plan_id,
                "user_id": user_id
            }]
        ).one_or_none()

        if not plan_result:
            raise HTTPException(status_code=404, detail="Plan does not exist for this user.")

        conn.execute(
            sqlalchemy.text(
                """
                DELETE FROM plan_items
                WHERE plan_id = :plan_id
                """
            ),
            [{"plan_id": plan_id}]
        )

        conn.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_plans
                WHERE id = :plan_id AND user_id = :user_id
                """
            ),
            [{
                "plan_id": plan_id,
                "user_id": user_id
            }]
        )

    return UserPlansRemovePlanResponse(
        plan_id=plan_id,
        status="removed"
    )
