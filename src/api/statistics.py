from fastapi import APIRouter, Depends, HTTPException
import sqlalchemy
from pydantic import BaseModel
from src.api import auth
from src import database as db
from enum import Enum
from datetime import date


router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    dependencies=[Depends(auth.get_api_key)],
)

class MacroTotalResponse(BaseModel):
    date:date
    calories: float
    calorie_progress: str
    protein: float
    protein_progress: str
    carbs: float
    carbs_progress: str
    fats: float
    fats_progress: str
    total_goals_met: int



@router.get("/{user_id}", response_model=None)
def get_daily_summary(user_id: int, summary_date: date):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM USERS 
                WHERE id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).one_or_none()

        if not result:
            raise HTTPException(status_code=404, detail="User does not exist.")

        macro_totals = connection.execute(
            sqlalchemy.text(
                """
                SELECT sum(calories) as total_calories, 
                       sum(protein) as total_protein, 
                       sum(carbs) as total_carbs, 
                       sum(fat) as total_fat
                FROM user_logs
                JOIN log_items on log_items.log_id = user_logs.id
                JOIN user_items on user_items.id = log_items.item_id
                WHERE user_logs.user_id = :user_id AND date = :summary_date
                """
            ),
            [{"user_id": user_id, "summary_date":summary_date}]
        ).one_or_none()

        if not macro_totals:
            raise HTTPException(status_code=404, detail="No results for this date.")

        calories = macro_totals.total_calories if macro_totals.total_calories else 0
        protein = macro_totals.total_protein if macro_totals.total_protein else 0
        carbs = macro_totals.total_carbs if macro_totals.total_carbs else 0
        fats = macro_totals.total_fat if macro_totals.total_fat else 0

        macro_goals = connection.execute(
            sqlalchemy.text(
                """
                SELECT nutrient, quantity, unit
                FROM macro_goal
                WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).all()

        protein_goal = -1
        carbs_goal = -1
        fats_goal = -1
        calories_goal = -1
        for row in macro_goals:
            if row.nutrient == "protein":
                protein_goal = row.quantity
            elif row.nutrient == "carbs":
                carbs_goal = row.quantity
            elif row.nutrient == "fats":
                fats_goal = row.quantity
            else:
                calories_goal = row.quantity

        protein_progress = protein / protein_goal * 100
        carbs_progress = carbs / carbs_goal * 100
        fats_progress = fats / fats_goal * 100
        calories_progress = calories / calories_goal * 100
        progress_bars = [protein_progress, carbs_progress, fats_progress, calories_progress]
        goals_met = sum([1 if progress > 100 else 0 for progress in progress_bars])

        return MacroTotalResponse(
            date=summary_date,
            calories=calories,
            calorie_progress=f"{round(calories_progress, 2)} %" if calories_progress >= 0 else "No Goal",
            protein=protein,
            protein_progress=f"{round(protein_progress, 2)} %" if protein_progress >= 0 else "No Goal",
            carbs=carbs,
            carbs_progress=f"{round(carbs_progress, 2)} %" if carbs_progress >= 0 else "No Goal",
            fats=fats,
            fats_progress=f"{round(fats_progress, 2)} %" if fats_progress >= 0 else "No Goal",
            total_goals_met = goals_met
        )










