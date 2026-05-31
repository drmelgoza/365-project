from enum import Enum
from collections import defaultdict
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db


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


class MealPlanCreate(BaseModel):
    name: str
    schedule_type: ScheduleType
    # days is only relevant for weekly or custom schedules
    days: Optional[list[str]] = None


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
    plan_id: int
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

class SamePlanResponse(BaseModel):
    user_name: str
    user_email: str
    


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

        # encode days into schedule string if provided (e.g. "weekly:monday,thursday")
        if new_plan.days:
            schedule_str = f"{new_plan.schedule_type.value}:{','.join(new_plan.days)}"
        else:
            schedule_str = new_plan.schedule_type.value

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
                "schedule": schedule_str
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
                    ui.fat
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
                plan_name=plan.name,
                schedule_type=str(plan.schedule_type),
                days=plan.days,
                category=plan.category,
                items=[
                    UserPlanItem(
                        name=r.name,
                        calories=r.calories,
                        protein=r.protein,
                        carbs=r.carbs,
                        fat=r.fat
                    )
                    for r in items_by_plan[plan.id]
                ]
            ))

    return response



#add plan id
@router.delete("/{user_id}/{plan_id}/items/{item_id}", response_model=UserPlansRemoveItemResponse)
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
            [{"user_id": user_id, "item_id": item_id}]
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

@router.get("/{user_id}", response_model=list[SamePlanResponse])
def compare_meal_plan(user_id: int):
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

    

        person = conn.execute(
            sqlalchemy.text(
                """
                SELECT id, name, schedule
                FROM user_plans
                WHERE user_id = :user_id
                ORDER BY id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not user_result:
            raise HTTPException(status_code=404, detail="User does not exist in eser_plans.")


        same = conn.execute(
            sqlalchemy.text(
                """
                SELECT user.name, user.email
                FROM user_plans
                JOIN users
                ON user.id = user_plans.user_id
                WHERE user_plans.schedule = :schedule
                ORDER BY id
                """
            ),
            [{"schedule": person.schedule}]
        ).all()

        print(f"Person with id {user_id} has the same plan as the following people")
        list_of_people = []
        for p in same:
            list_of_people.append(SamePlanResponse(
                user_name = p.name,
                user_email = p.email
            )
            )
        

    return list_of_people