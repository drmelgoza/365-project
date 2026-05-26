# New Test Cases

## Test Case #1: User Stats Update
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

## Test Case #2: Basic Flow Test
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

***Observation:*** Basic flow seems to be working. Test cases return expected results.

## Test Case #3: Invalid Date Formatting

Tests validation of negative input values.

```bash
curl -i -X POST "http://127.0.0.1:3000/users/2/items" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{"name":"Negative Food","calories":-100,"protein":-5,"carbs":-10,"fat":-2}'
```

Result:
```json
{"detail":[{"type":"greater_than_equal","loc":["body","calories"],"msg":"Input should be greater than or equal to 0","input":-100,"ctx":{"ge":0.0}},{"type":"greater_than_equal","loc":["body","protein"],"msg":"Input should be greater than or equal to 0","input":-5,"ctx":{"ge":0.0}},{"type":"greater_than_equal","loc":["body","carbs"],"msg":"Input should be greater than or equal to 0","input":-10,"ctx":{"ge":0.0}},{"type":"greater_than_equal","loc":["body","fat"],"msg":"Input should be greater than or equal to 0","input":-2,"ctx":{"ge":0.0}}]}
```
***Observation:*** Code has been corrected to check for negative values and the result is the correct
expected result.

## Test Case #4: Invalid Dates

Tests invalid date formatting.

>**NOTE:** Original test case body was replaced with new request
> body that matches new date format.

```bash
curl -i -X POST "http://127.0.0.1:3000/users/2/logs" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
	  "date": "2026-26-05",
	  "category": "breakfast"
	}'
```

Result:

```json
{"detail":[{"type":"date_from_datetime_parsing","loc":["body","date"],"msg":"Input should be a valid date or datetime, month value is outside expected range of 1-12","input":"2026-26-05","ctx":{"error":"month value is outside expected range of 1-12"}}]}
```

***Observation:*** Invalid date format returns error as expected. Test case works.

## Test Case #5: Duplicate Items

This test case tests duplicate items.

> [!IMPORTANT]
> This test case is expected to change.

>**NOTE:** Schema might be reworked to handle this

```bash
curl -i -X POST "http://127.0.0.1:3000/logs/2/items?user_id=1" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{"item_ids":[4,4]}'
```

Result:

```json
{"item_ids":[4,4],"status":"logged"}
```
***Observation:*** Currently returns as successful, as expected.
Result may be expected to change with new implementation for
the logs endpoint.

## Test Case #6: Deletion of non-existent item

This test checks to see if an error returns for
attempting to delete a non-existent item for a specific user.

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:3000/plans/1/plan/items/8' \
  -H 'accept: application/json' \
  -H 'access_token: ***'
```

Result:

```json
{"detail":"Item does not exist in this user's plan."}
```

***Observation:*** Test returns as expected. An 404 error
returns signaling that the item doesn't exist.