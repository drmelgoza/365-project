import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
from datetime import date, timedelta
import random

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

foods = [
    ("Chicken Breast", 165, 31, 0, 3.6),
    ("Brown Rice", 216, 5, 45, 1.8),
    ("Greek Yogurt", 100, 17, 6, 0.7),
    ("Oatmeal", 154, 5, 27, 2.5),
    ("Salmon", 208, 20, 0, 13),
    ("Eggs", 78, 6, 1, 5),
    ("Sweet Potato", 103, 2, 24, 0.1),
    ("Almonds", 164, 6, 6, 14),
    ("Banana", 89, 1, 23, 0.3),
    ("Tuna", 132, 29, 0, 1),
    ("Avocado", 240, 3, 12, 22),
    ("Peanut Butter", 188, 8, 6, 16),
    ("Black Beans", 227, 15, 41, 0.9),
    ("Protein Shake", 150, 25, 8, 3),
    ("Broccoli", 55, 4, 11, 0.6),
]
meal_categories = ["breakfast", "lunch", "dinner", "snack", "supper"]
schedule_types = ["daily", "weekly", "custom"]
# days used when schedule_type is weekly or custom
weekday_options = [
    ["monday", "wednesday", "friday"],
    ["tuesday", "thursday"],
    ["monday", "tuesday", "wednesday", "thursday", "friday"],
    ["monday", "friday"],
    [],
]
plan_names = ["Bulking Plan", "Cutting Plan", "Maintenance", "High Protein", "Low Carb", "Keto"]
height_units = ["ft/in", "cm"]
weight_units = ["lbs", "kg"]
units = ["g", "oz", "cup", "tbsp", "serving"]

num_users = 10_000
fake = Faker()

# negative binomial gives a realistic skewed distribution — most users have few,
# a small number of power users have many (same idea as prof's posts distribution)
items_sample_distribution = np.random.default_rng().negative_binomial(1, 0.09, num_users).clip(3, 30)  # avg ~10
logs_sample_distribution = np.random.default_rng().negative_binomial(2, 0.07, num_users).clip(5, 60)  # avg ~25
plans_sample_distribution = np.random.default_rng().negative_binomial(1, 0.40, num_users).clip(1, 3)  # avg ~1.5

total_log_items = 0
total_plan_items = 0

# create fake users with items, logs, and plans
with engine.begin() as conn:
    print("creating fake users...")
    all_items = []
    all_logs = []
    all_log_items = []
    all_plans = []
    all_plan_items = []

    for i in range(num_users):
        if (i % 1000 == 0):
            print(i)

        h_unit = random.choice(height_units)
        w_unit = random.choice(weight_units)
        height = round(random.uniform(155, 200), 1) if h_unit == "cm" else round(random.uniform(60, 78), 1)

        user_id = conn.execute(sqlalchemy.text("""
            INSERT INTO users (username, name, email, height, height_unit, weight, weight_unit, age)
            VALUES (:username, :name, :email, :height, :height_unit, :weight, :weight_unit, :age)
            RETURNING id;
        """), {
            "username": fake.unique.user_name(),
            "name": fake.name(),
            "email": fake.unique.email(),
            "height": height,
            "height_unit": h_unit,
            "weight": round(random.uniform(50, 110), 1),
            "weight_unit": w_unit,
            "age": random.randint(18, 70),
        }).scalar_one()

        num_items = items_sample_distribution[i]
        for _ in range(num_items):
            food = random.choice(foods)
            all_items.append({
                "user_id": user_id,
                "name": food[0],
                "calories": food[1],
                "protein": food[2],
                "carbs": food[3],
                "fat": food[4],
            })

        num_logs = logs_sample_distribution[i]
        for _ in range(num_logs):
            all_logs.append({
                "user_id": user_id,
                "date": date.today() - timedelta(days=random.randint(0, 365)),
                "category": random.choice(meal_categories),
            })

        num_plans = plans_sample_distribution[i]
        used_names = set()
        for _ in range(num_plans):
            name = random.choice(plan_names)
            while name in used_names:
                name = random.choice(plan_names)
            used_names.add(name)
            stype = random.choice(schedule_types)
            days = random.choice(weekday_options) if stype in ("weekly", "custom") else []
            all_plans.append({
                "user_id": user_id,
                "name": name,
                "schedule_type": stype,
                "days": days,
            })

    if all_items:
        conn.execute(sqlalchemy.text("""
            INSERT INTO user_items (user_id, name, calories, protein, carbs, fat)
            VALUES (:user_id, :name, :calories, :protein, :carbs, :fat);
        """), all_items)
        result = conn.execute(sqlalchemy.text("SELECT id, user_id FROM user_items"))
        user_item_map = {}
        for item_id, uid in result:
            user_item_map.setdefault(uid, []).append(item_id)

    if all_logs:
        conn.execute(sqlalchemy.text("""
            INSERT INTO user_logs (user_id, date, category)
            VALUES (:user_id, :date, :category);
        """), all_logs)
        result = conn.execute(sqlalchemy.text("SELECT id, user_id FROM user_logs"))
        for log_id, uid in result:
            pool = user_item_map.get(uid, [])
            if not pool:
                continue
            for item_id in random.sample(pool, min(random.randint(1, 3), len(pool))):
                all_log_items.append({
                    "log_id": log_id,
                    "item_id": item_id,
                    "quantity": random.randint(1, 3),
                    "unit": random.choice(units),
                })
                total_log_items += 1

    if all_log_items:
        conn.execute(sqlalchemy.text("""
            INSERT INTO log_items (log_id, item_id, quantity, unit) VALUES (:log_id, :item_id, :quantity, :unit);
        """), all_log_items)

    if all_plans:
        conn.execute(sqlalchemy.text("""
            INSERT INTO user_plans (user_id, name, schedule_type, days)
            VALUES (:user_id, :name, :schedule_type, :days);
        """), all_plans)
        result = conn.execute(sqlalchemy.text("SELECT id, user_id FROM user_plans"))
        for plan_id, uid in result:
            pool = user_item_map.get(uid, [])
            if not pool:
                continue
            for item_id in random.sample(pool, min(10, len(pool))):
                all_plan_items.append({
                    "plan_id": plan_id,
                    "item_id": item_id,
                    "category": random.choice(meal_categories),
                    "quantity": random.randint(1, 3),
                    "unit": random.choice(units),
                })
                total_plan_items += 1

    if all_plan_items:
        conn.execute(sqlalchemy.text("""
            INSERT INTO plan_items (plan_id, item_id, category, quantity, unit)
            VALUES (:plan_id, :item_id, :category, :quantity, :unit);
        """), all_plan_items)

    print("total users: ", num_users)
    print("total user_items: ", len(all_items))
    print("total user_logs: ", len(all_logs))
    print("total log_items: ", total_log_items)
    print("total user_plans: ", len(all_plans))
    print("total plan_items: ", total_plan_items)
