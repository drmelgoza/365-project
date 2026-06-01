# API Specification for Data-Fit

> **Naming convention:** all endpoints use **snake_case** path parameters and **snake_case** JSON field names.

---

# 1. Users

Users represent a health profile inside Data-Fit. All user data (logs, items, plans) is scoped to a `user_id`.

## Flow Order

1. Create User
2. Get User
3. Update User (optional)
4. Delete User (optional)

## 1.1 Create User — `POST /users/`

Create a new user profile.

### Request

```json
{
  "username": "karate_kid_84",
  "name": "Daniel",
  "email": "daniel@somemail.com",
  "height": 68,
  "height_unit": "ft/in",
  "weight": 125,
  "weight_unit": "lbs",
  "age": 19
}
```

> `height` and `weight` must be ≥ 0. `age` must be a non-negative integer. `email` must be a valid e-mail address.

> `height`, when using the `"ft\in"` height unit can be input in either inches (e.g. 60 in) or in foot-inch format (e.g. 5'0")

### Response `200`

```json
{
  "user_id": 20
}
```

### Error Responses

- `409 Conflict`: A user with this e-mail already exists.
- `400 Bad Request`: Invalid values for height or weight is inputted. 

---

## 1.2 Get User — `GET /users/{user_id}`

Retrieve a user's profile information.

### Response `200`

```json
{
  "username": "karate_kid_84",
  "name": "Daniel",
  "email": "daniel@somemail.com",
  "height": 68,
  "height_unit": "ft/in",
  "weight": 125,
  "weight_unit": "lbs",
  "age": 19
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

## 1.3 Update User — `PATCH /users/{user_id}`

Update one or more of a user's physical stats. Only fields provided (non-null) are updated.

### Request

```json
{
  "height": 70
}
```

> Omit any field you do not wish to change. All provided values must be ≥ 0.

### Response `200`

```json
{
  "user_id": 20,
  "updated_values": [{
    "height": 70
  }],
  "status": "updated"
}
```

---

## 1.3 Delete User — `DELETE /users/{user_id}`

Delete an entire user profile and all of its related information. All logs, plans, food items, and goals from this user will also be deleted with it.

### Response `200`

```json
{
  "user_id": 20,
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

# 2. Food Items

Users maintain a personal library of food items with their macro-nutrient facts. Items are referenced when logging meals.

## Flow Order

1. Create Food Item
2. Get Food Items
3. Update Food Item (optional)
4. Delete Food Item (optional)

## 2.1 Create Food Item — `POST /users/{user_id}/items`

Add a food item to a user's personal library. 

> Food items are considered to be a single unit. Quantities can be added to items later when adding them to meal logs.

### Request

```json
{
  "name": "Johnny's Family Omelette",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```

> All nutritional values must be ≥ 0.

### Response `200`

```json
{
  "user_id": 4567,
  "item_id": 1231,
  "status": "created"
}
```

### Error Responses

- `404 Not Found`: User does not exist.
- `400 Bad Request`: Input values are not valid.

---

## 2.2 Get Food Items — `GET /users/{user_id}/items`

Get all food items for a specific user.

### Response `200`

```json
{
  "user_id": 21,
  "items": [
    {
        "name": "Johnny's Family Omelette",
        "calories": 450,
        "protein": 35,
        "carbs": 20,
        "fat": 15
    },
    {
        "name": "Granny's Golden Pancakes",
        "calories": 600,
        "protein": 15,
        "carbs": 40,
        "fat": 25
    }
  ]
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

## 2.3 Update Food Item — `PATCH /users/{user_id}/items/{item_id}`

Update a specific food item for a specific user.

> Omit any field you do not wish to change. All provided numeric values must be ≥ 0.

### Request

```json
{
  "calories": 680
}
```

### Response `200`

```json
{
  "user_id": 67,
  "item_id": 123,
  "changed_values": {
    "calories": 680
  },
  "status": "updated"
}
```

### Error Responses

- `404 Not Found`: User or Item does not exist.
- `400 Bad Request`: Numeric values are not valid.

---

## 2.4 Delete Food Item — `DELETE /users/{user_id}/items/{item_id}`

Delete a specific food item for a specific user.

### Response `200`

```json
{
  "user_id": 123,
  "item_id": 92,
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: User or Item does not exist.

---

# 3. Meal Logs

A meal log groups food items by both category and date for later viewing and analysis.

## Flow Order

1. Create a Meal Log
2. Add a Food Item to a Log
3. Get a Meal Log (to verify)
4. Remove Item from Log (if needed)
5. Delete a Meal Log (optional)

## 3.1 Create Meal Log — `POST /users/{user_id}/logs`

### Request

```json
{
  "date": "2026-05-22",
  "category": "breakfast"
}
```

> `date` must be in ISO 8601 format (`YYYY-MM-DD`).  
> `category` must be one of: `breakfast`, `lunch`, `dinner`, `snack`, `supper`.

### Response `200`

```json
{
  "log_id": 7
}
```

---

## 3.2 Add a Food Item to a Log — `POST /users/{user_id}/logs/{log_id}/items`

Add a food item to an existing meal log.

### Request

```json
{
  "item_id": 12,
  "quantity": 1,
  "unit": "stack"
}
```

### Response `200`

```json
{
  "status": "logged"
}
```

### Error Responses

- `404 Not Found`: User, log, or item does not exist.

---

## 3.3 Get a Meal Log — `GET /users/{user_id}/logs`

Retrieve the log metadata and all items in a meal log. Searching can be done by log category, by date, or by the id of the log.

### Request

```json
{
  "log_date": "2026-05-22"
}
```

### Response `200`

```json
{
  "results": [
    {
      "date": "2026-05-31",
      "logs": [
        {
          "id_and_category": "id 1: breakfast",
          "items": [
            {
              "id": 123,
              "name": "Granny's Golden Pancakes",
              "quantity": "1 stack",
              "calories": 500,
              "protein": 15,
              "carbs": 50,
              "fat": 12
            },
            {
              "id": 124,
              "name": "Spicy Fried Eggs",
              "quantity": "1 serving",
              "calories": 250,
              "protein": 20,
              "carbs": 12,
              "fat": 10
            }
          ]
        }
      ]
    }
  ]
}
```

### Error Responses

- `404 Not Found`: User or log does not exist.

---


## 3.4 Remove Item from Log — `DELETE users/{user_id}/logs/{log_id}/items/{item_id}`

Remove a specific food item from a meal log.

### Response `200`

```json
{
  "user_id": 12,
  "log_id": 21,
  "item_id": 20,
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: User, Log, or Item does not exist.

---

## 3.5 Delete a Meal Log — `DELETE users/{user_id}/logs/{log_id}`

Remove a specific a meal log for a user. Items that existed in the meal log will still exist for the user.

### Response `200`

```json
{
  "user_id": 12,
  "log_id": 1,
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: User or Log does not exist.

---

# 4. Meal Plans

Meal plans let users organize recurring eating schedules.

## Flow Order

1. Create Plan
2. Get All Plans
3. Delete Plan (if needed)

## 4.1 Create Plan — `POST /plans/{user_id}/plan`

### Request

```json
{
  "name": "Cutting Plan",
  "schedule_type": "daily"
}
```

Weekly / custom example:

```json
{
  "name": "Gym Days",
  "schedule_type": "weekly",
  "days": ["monday", "thursday", "friday"]
}
```

> `schedule_type` must be one of: `daily`, `weekly`, `custom`.  
> `days` is optional and only meaningful for `weekly` or `custom` schedules.

### Response `200`

```json
{
  "plan_id": 1,
  "user_id": 20,
  "name": "Cutting Plan",
  "schedule": "daily"
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

## 4.2 Get All Plans — `GET /plans/{user_id}/plan`

Returns **all** meal plans for the user (not just the first one).

> [!NOTE] 
> This section (4.2) expected to change.

### Response `200`

```json
[
  {
    "plan_id": 1,
    "user_id": 20,
    "plan_name": "Cutting Plan",
    "schedule_type": "daily",
    "items": ["..."]
  },
  {
    "plan_id": 2,
    "user_id": 20,
    "plan_name": "Gym Days",
    "schedule_type": "weekly:monday,thursday,friday",
    "items": ["..."]
  }
]
```

### Error Responses

- `404 Not Found`: User does not exist.

---

## 4.3 Delete Plan — `DELETE /plans/{user_id}/plan/{plan_id}`

### Response `204 No Content`

### Error Responses

- `404 Not Found`: Plan not found for this user.

---

# 5. Macro Goals

Macro goals are used to track daily progress across meal logs for desired nutrients.

## Flow Order
1. Add a Macro Goal
2. Get all Macro Goals
3. Update a Macro Goal (optional)
4. Delete a Macro Goal (optional)

---

## 5.1 Add a Macro Goal — `POST /users/{user_id}/goals`

Add a macro goal for a specific user.

### Request

```json
{
  "nutrient": "protein",
  "quantity": 20
}
```

> Goals for macronutrients (protein, carbs, etc.) are automatically assumed to be in grams (g), while goals for calories are automatically assumed to be in calories (kcal).

### Response `200`

```json
{
  "user_id": 22,
  "status": "created"
}
```

>If a macro goal already exists for the specified category, `status` will be returned as `"goal already exists"` and no edits will be made. To edit a macro goal, use the endpoint `PATCH /users/{user_id}/goals`.

### Error Responses

- `404 Not Found`: User does not exist.
- `400 Bad Request`: Numeric values are not valid.

---

## 5.2 Get all Macro Goals — `GET /users/{user_id}/goals`

Retrieve all macro goals for a specific user. If no goal exists for a specific category, it will not be included.

### Response `200`

```json
{
  "user_id": 21,
  "goals": [
    {
      "nutrient": "protein",
      "quantity": 130,
      "unit": "g"
    },
    {
      "nutrient": "calories",
      "quantity": 2200,
      "unit": "kcal"
    }
  ]
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---
## 5.3 Update a Macro Goal — `PATCH /users/{user_id}/goals/{goal}`

Update a specific macro goal for a specific user.

### Request

```json
{
  "quantity": 125
}
```

### Response `200`

```json
{
  "user_id": 21,
  "category": "protein",
  "new_value": 125,
  "status": "updated"
}
```

### Error Responses

- `404 Not Found`: User or Goal does not exist.

---
## 5.4 Delete a Macro Goal — `DELETE /users/{user_id}/goals/{goal}`

Delete a Macro Goal for a specific user.

### Response `200`

```json
{
  "user_id": 22,
  "goal": "protein",
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: User or Goal does not exist.

---

# 6. Statistics

Return nutrient summaries and goal progress for a specific day's meal logs.

## Flow Order
1. Get Daily Summary

## 6.1 Get Daily Summary - `GET users/{user_id}/statistics`

Get the total amount consumed in a day for each macronutrient, and retrieve the goal percent-completion for that macronutrient. Macronutrients with no goal will instead display `"No Goal"`

### Request:

```json
{
  "date": "2026-04-01"
}
```

### Response `200`:

```json
{
  "date": "2026-04-01",
  "calories": 1100,
  "calorie_progress": "55.0 %",
  "protein": 325,
  "protein_progress": "250.0 %",
  "carbs": 60,
  "carbs_progress": "No Goal",
  "fats": 30,
  "fats_progress": "75.0 %",
  "total_goals_met": 1
}
```

### Error Responses:
- `404 Not Found`: User does not exist.

---

# 7. Admin

## 7.1 Reset Database — `POST /admin/reset`

Truncates all tables and resets serial sequences. **Destructive — use with caution.**

### Response `204 No Content`