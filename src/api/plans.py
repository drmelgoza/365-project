from enum import Enum
from collections import defaultdict
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

class Macro(str, Enum):
    OPTION_1 = "protien"
    OPTION_2 = "carbs"
    OPTION_3 = "fats"


class Category(str, Enum):
    OPTION_1 = "breakfast"
    OPTION_2 = "lunch"
    OPTION_3 = "dinner"
    OPTION_4 = "snack"
 

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    dependencies=[Depends(auth.get_api_key)],
)


#models

class ScheduleType(str, Enum):
    daily = "daily"
    weekly = "weekly"
    custom = "custom"

class CategoryType(str, Enum):
    breakfast = "breakfast",
    lunch = "lunch",
    dinner = "dinner",
    snack = "snack",
    supper = "supper"

class DayType(str, Enum):
    monday = "monday",
    tuesday = "tuesday",
    wednesday = "wednesday",
    thursday = "thursday",
    friday = "friday"

class UnitType(str, Enum):
    gram = "g",
    ounces = "oz",
    tbsp = "tbsp",
    serving = "serving"


class MealPlanCreate(BaseModel):
    name: str
    schedule_type: ScheduleType
    category: CategoryType
    # days is only relevant for weekly or custom schedules
    days: Optional[list[DayType]] = None


class MealPlanCreateResponse(BaseModel):
    plan_id: int
    user_id: int
    status: str


class MealPlanAdd(BaseModel):
    item_id: int
    quantity: int = 1
    unit_type: UnitType


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
    quantity: int


class UserPlansLogResponse(BaseModel):
    plan_id: int
    user_id: int
    plan_name: str
    schedule_type: str
    days: list[str]
    category: CategoryType
    items: list[UserPlanItem]


class UserPlansRemoveItemResponse(BaseModel):
    item_id: int
    status: str


class UserPlansRemovePlanResponse(BaseModel):
    plan_id: int
    status: str

class UserMacro(BaseModel):
    name: str
    type: float


    


#endpoints

@router.post("/{user_id}", response_model=MealPlanCreateResponse)
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
                INSERT INTO user_plans (user_id, name, schedule_type, days, category)
                VALUES (:user_id, :name, :schedule_type, :days, :category)
                RETURNING id
                """
            ),
            [{
                "user_id": user_id,
                "name": new_plan.name,
                "schedule_type": new_plan.schedule_type,
                "days": new_plan.days,
                "category": new_plan.category
            }]
        ).one()

    return MealPlanCreateResponse(
        plan_id=plan_result.id,
        user_id=user_id,
        status="created"
    )


@router.post("/{user_id}/{plan_id}/items", response_model=MealPlanAddResponse)
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
            [{"plan_id": plan_id, "user_id": user_id}]
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
            [{"item_id": new_item.item_id, "user_id": user_id}]
        ).one_or_none()

        if not item_result:
            raise HTTPException(status_code=404, detail="Item does not exist for this user.")

        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO plan_items (plan_id, item_id, quantity, unit)
                VALUES (:plan_id, :item_id, :quantity, :unit_type)
                """
            ),
            [{
                "plan_id": plan_id,
                "item_id": new_item.item_id,
                "quantity": new_item.quantity,
                "unit_type": new_item.unit_type
            }]
        )

    return MealPlanAddResponse(
        plan_id=plan_id,
        item_id=new_item.item_id,
        user_id=user_id,
        status="items added"
    )


@router.get("/{user_id}/plan", response_model=list[UserPlansLogResponse])
def get_meal_plan(
        user_id: int,
        category: list[CategoryType] | None = Query(None),
        days: list[DayType] | None = Query(None)
):
    """Return all plans for the user instead of just the first one."""
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

        query = """
            SELECT DISTINCT
                up.id,
                up.user_id,
                up.name,
                up.schedule_type,
                up.days,
                up.category
            FROM user_plans up
            JOIN plan_items pi ON pi.plan_id = up.id
            WHERE up.user_id = :user_id
        """

        params: dict[str, Any] = {"user_id": user_id}

        if category:
            query += """ 
                AND up.category = ANY(:categories)
            """
            params["categories"] = [c.value for c in category]

        if days:
            query += """ 
                AND up.days && :days
            """
            params["days"] = [d.value for d in days]

        plans = conn.execute(
            sqlalchemy.text(query),
            params
        ).all()

        plan_ids = [plan.id for plan in plans]

        if not plan_ids:
            return []

        items_result = conn.execute(
            sqlalchemy.text(
                """
                SELECT
                    pi.plan_id,
                    ui.name,
                    ui.calories,
                    ui.protein,
                    ui.carbs,
                    ui.fat,
                    pi.quantity
                FROM plan_items pi
                JOIN user_items ui ON pi.item_id = ui.id
                WHERE pi.plan_id = ANY(:plan_ids)
                """
            ),
            {"plan_ids": plan_ids}
        ).all()

        response = []

        items_by_plan = defaultdict(list)

        for row in items_result:
            items_by_plan[row.plan_id].append(row)

        for plan in plans:

            response.append(UserPlansLogResponse(
                plan_id=plan.id,
                user_id=plan.user_id,
                plan_name=plan.name,
                schedule_type=str(plan.schedule_type),
                days=plan.days,
                category=plan.category,
                items=[
                    UserPlanItem(
                        name=r.name,
                        calories= round(r.calories * r.quantity, 2),
                        protein= round(r.protein * r.quantity, 2),
                        carbs= round(r.carbs * r.quantity, 2),
                        fat= round(r.fat * r.quantity, 2),
                        quantity=r.quantity
                    )
                    for r in items_by_plan[plan.id]
                ]
            ))

    return response



#add plan id
@router.delete("/{user_id}/{plan_id}/items/{item_id}", response_model=UserPlansRemoveItemResponse)
def remove_item_from_plan(user_id: int, plan_id: int, item_id: int):
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
                FROM user_plans up
                WHERE up.id = :plan_id AND up.user_id = :user_id
                """
            ),
            {"plan_id": plan_id, "user_id": user_id}
        ).one_or_none()

        if not plan_result:
            raise HTTPException(status_code=404, detail="Plan does not exist for this user.")

        #TODO: Change ".all" to ".one_or_none()" after adding a check for duplicate items in meal plan
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
            [{"user_id": user_id, "item_id": item_id}]
        ).all()

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
            [{"user_id": user_id, "item_id": item_id}]
        )

    return UserPlansRemoveItemResponse(item_id=item_id, status="removed")


@router.delete("/{user_id}/{plan_id}", response_model=UserPlansRemovePlanResponse)
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
            [{"plan_id": plan_id, "user_id": user_id}]
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
            [{"plan_id": plan_id, "user_id": user_id}]
        )

    return UserPlansRemovePlanResponse(plan_id=plan_id, status="removed")


###DAVID WORK
###ADDED an API that matches a person with other people who share the same meal_plan 

@router.get("/{user_id}/plan", response_model=list[UserMacro])
def item_tracker_per_category(user_id: int, macro: Macro, category: Category): 
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
    
        tracker = conn.execute(
            sqlalchemy.text(
                f"""
                select  user_items.user_id, name, {macro} as type
                form user_items
                JOIN log_items
                ON user_items.id = log_items.item_id
                Join user_logs
                On user_items.user_id = user_logs.user_id and user_logs.id = log_items.log_id
                WHERE user_id = :user_id and user_logs.category = :category
                """

            ),
            {"user_id": user_id,
             "category": category}
        ).all()

        list_of_macro = []
        for item in tracker:
            food = UserMacro(
                name= item.name,
                type= item.type
            )
            list_of_macro.append(food)
        
        return list_of_macro
        
        
        
    