# New Test Cases

## Test Case #1
This test is testing that the PATCH endpoint is working correctly to update user stats.

Curl command:

```bash
curl -X POST \
 "https://datafit-meal-tracker.onrender.com/users/" \
 -H "accept: application/json" \
 -H "access_token: ***" \
 -H "Content-Type: application/json" \
 -d '{
 "username": "viciswoozy",
 "name": "Victor",
 "email": "victor@somemail.com",
 "height": 70,
 "weight": 185,
 "age": 20
}'
```

Result for creation:

```json
{"user_id":11}
```

Curl command for updating users stats:

```bash
curl -X PATCH \
  "https://datafit-meal-tracker.onrender.com/users/11" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 100
  }'
```

Results for updating:

```json
{"user_id":11,"status":"updated"}
```

## Test Case #2
* Attempt to add an item to the meal plan
* Get the meal plan
* Get meal plans by category and by day and ensure their correctness
* Log item to the log
* Verify numbers, check for duplicate or inconsistent values like null, 0, or empty and blank,
* Delete item from log
* Remove the single item from the plan and erase the plan completely
* Check if logs and meal plans are truly empty and deleted.

**User adds item to their profile (Curl command):**

```bash
curl -X POST \
  "https://datafit-meal-tracker.onrender.com/users/10/items" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hamburger",
    "calories": 910,
    "protein": 20,
    "carbs": 30,
    "fat": 20
  }'
```
Result:
```json
{"item_id":9,"user_id":10,"status":"created"}
```
**User adds item from their available items to a new/existing meal plan:**
```bash
curl -X POST \
  "https://datafit-meal-tracker.onrender.com/plans/10/plan" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daniel'\''s workout plan",
    "schedule": "weekly",
    "days": [
      "Monday", 
      "Wednesday"
    ]
  }'
```

Result from creating plan:
```json
{"plan_id":6,"user_id":10,"status":"created"}
```

User actually adds item:
```bash
curl -X POST \
  "https://datafit-meal-tracker.onrender.com/plans/10/plan/6/items" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 9,
    "category": "Lunch"
  }'
```

Result:
```json
{"plan_id":6,"item_id":9,"user_id":10,"status":"items added"}
```

**User gets plans altogether and then by both day and category:**

Get meal plan normally:
```bash
curl -X GET \
  "https://datafit-meal-tracker.onrender.com/plans/10/plan" \
  -H "accept: application/json" \
  -H "access_token: ***"
```

Result:
```json
{"day":"Daniel's workout plan","time":"weekly","category":"Lunch","items":[{"name":"Hamburger","calories":910.0,"protein":20.0,"carbs":30.0,"fat":20.0}]}
```

**Get meal plan by day:**
```bash
curl -X GET \
  "https://datafit-meal-tracker.onrender.com/plans/10/plan/day?plan_name=Daniel's%20workout%20plan" \
  -H "accept: application/json" \
  -H "access_token: ***"
```

Result:
```json
{"plan_name":"Daniel's workout plan","schedule":"weekly","items":[{"name":"Hamburger","calories":910.0,"protein":20.0,"carbs":30.0,"fat":20.0}]}
```

**Get meal plan by category:**
```bash
curl -X GET \
  "https://datafit-meal-tracker.onrender.com/plans/10/plan/category?category=Lunch" \
  -H "accept: application/json" \
  -H "access_token: ***"
```

Result:
```json
{"category":"Lunch","schedule":"weekly","items":[{"name":"Hamburger","calories":910.0,"protein":20.0,"carbs":30.0,"fat":20.0}]}
```

## Test Case #3
