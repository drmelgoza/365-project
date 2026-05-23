# API Specification for Data-Fit

> **Naming convention:** all endpoints use **snake_case** path parameters and **snake_case** JSON field names.

---

# 1. Users

Users represent a health profile inside Data-Fit. All user data (logs, items, plans) is scoped to a `user_id`.

## Flow Order

1. Create User
2. Get User
3. Update User (optional)

## 1.1 Create User — `POST /users/`

Create a new user profile.

### Request

```json
{
  "username": "karate_kid_84",
  "name": "Daniel",
  "email": "daniel@somemail.com",
  "height": 68,
  "weight": 125,
  "age": 19
}
```

> `height` and `weight` must be ≥ 0. `age` must be a non-negative integer. `email` must be a valid e-mail address.

### Response `200`

```json
{
  "user_id": 20
}
```

### Error Responses

- `409 Conflict`: A user with this e-mail already exists.

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
  "weight": 125,
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
  "status": "updated"
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

# 2. Food Items

Users maintain a personal library of food items with their macro-nutrient facts. Items are referenced when logging meals.

## 2.1 Create Food Item — `POST /users/{user_id}/items`

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
  "item_id": 1231,
  "user_id": 4567,
  "status": "created"
}
```

### Error Responses

- `404 Not Found`: User does not exist.

---

# 3. Meal Logs

A meal log groups food items eaten during a single meal category on a given date.

## Flow Order

1. Create Meal Log
2. Add Item(s) to Log
3. Get Log (to verify)
4. Remove Item from Log (if needed)

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

## 3.2 Add Items to Log — `POST /users/{user_id}/logs/{log_id}/items`

Add one or more food items to an existing meal log.

### Request

```json
{
  "item_ids": [1231, 3213]
}
```

### Response `200`

```json
{
  "status": "items added"
}
```

### Error Responses

- `404 Not Found`: Log or one of the items does not exist.

---

## 3.3 Get Log — `GET /users/{user_id}/logs/{log_id}`

Retrieve the log metadata and all items in a meal log.

### Response `200`

```json
{
  "category": "breakfast",
  "date": "2026-05-22",
  "items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    }
  ]
}
```

### Error Responses

- `404 Not Found`: User or log does not exist.

---

## 3.4 Add Item to Log (via log router) — `POST /logs/{log_id}/items?item_id={item_id}`

Alternative endpoint to add a single item to a log.

### Response `200`

```json
{
  "item_id": 1231,
  "log_id": 7,
  "status": "logged"
}
```

---

## 3.5 Remove Item from Log — `DELETE /logs/{log_id}/items/{item_id}`

Remove a specific food item from a meal log.

### Response `200`

```json
{
  "status": "deleted"
}
```

### Error Responses

- `404 Not Found`: Log does not exist, or item was not in this log.

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

### Response `200`

```json
[
  {
    "plan_id": 1,
    "user_id": 20,
    "name": "Cutting Plan",
    "schedule": "daily"
  },
  {
    "plan_id": 2,
    "user_id": 20,
    "name": "Gym Days",
    "schedule": "weekly:monday,thursday,friday"
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

# 5. Admin

## 5.1 Reset Database — `POST /admin/reset`

Truncates all tables and resets serial sequences. **Destructive — use with caution.**

### Response `204 No Content`
