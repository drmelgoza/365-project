# Flow 2: Meal Logging

## Scenario:
Joseph has just begun using DataFit, and has just finished his breakfast for the day.
To keep up with his protein goal, he must now add the meal into the DataFit meal log.

## Steps:
- Joseph wants to add his favorite breakfast omelette to track with DataFit. Joseph calls `POST /users/4567/items` to add the omelette.

```
{
  "name": "Johnny's Family Omelette",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```

- After being created the omelette's new item id is returned:
```
{
  "item_id": 1231,
  "user_id": 4567,
  "status": "created"
}
```

- Using his userid and the needed item id, Joseph calls `POST /users/4567/logs` to create a meal log for breakfast:
```
{
  "month": 1,
  "day": 1,
  "year": 2021,
  "time": "8:30",
  "category": "Breakfast"
}
```

- Joseph receives the following output:
```
{
  "log_id": 1
}
```

- Joseph links the omelette to his log using `POST /users/4567/logs/1/items`:
```
{
  "item_ids": [1231]
}
```

- Joseph forgot to log the breakfast sausage that he had as a side. He creates the sausage item first with `POST /users/4567/items`:
```
{
  "name": "Super Healthy Sausage",
  "calories": 450,
  "protein": 30,
  "carbs": 20,
  "fat": 20
}
```

- He retrieves the new item id:
```
{
  "item_id": 3213,
  "user_id": 4567,
  "status": "created"
}
```

- And links it to the same log with `POST /users/4567/logs/1/items`:
```
{
  "item_ids": [3213]
}
```

- Joseph confirms the final log has both items using `GET /users/4567/logs/1`:
```
{
  "category": "Breakfast",
  "month": 1,
  "day": 1,
  "year": 2021,
  "time": "08:30:00",
  "items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    },
    {
      "name": "Super Healthy Sausage",
      "calories": 450,
      "protein": 30,
      "carbs": 20,
      "fat": 20
    }
  ]
}
```

---

# Test Results

## Flow 2

Tested locally against `http://localhost:8000` with API key `tusk`.

1. `POST /users/{user_id}/items` (omelette)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"name": "Johnny'\''s Family Omelette", "calories": 450, "protein": 35, "carbs": 20, "fat": 15}'
   ```

   2. Result:
   ```
   {"item_id":5,"user_id":1,"status":"created"}
   ```

2. `POST /users/{user_id}/logs` (create breakfast log)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/logs' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"month": 1, "day": 1, "year": 2021, "time": "08:30", "category": "Breakfast"}'
   ```

   2. Result:
   ```
   {"log_id":3}
   ```

3. `POST /users/{user_id}/logs/{log_id}/items` (link omelette to log)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/logs/3/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"item_ids": [5]}'
   ```

   2. Result:
   ```
   {"status":"items added"}
   ```

4. `POST /users/{user_id}/items` (sausage)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"name": "Super Healthy Sausage", "calories": 450, "protein": 30, "carbs": 20, "fat": 20}'
   ```

   2. Result:
   ```
   {"item_id":6,"user_id":1,"status":"created"}
   ```

5. `POST /users/{user_id}/logs/{log_id}/items` (link sausage to log)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/logs/3/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"item_ids": [6]}'
   ```

   2. Result:
   ```
   {"status":"items added"}
   ```

6. `GET /users/{user_id}/logs/{log_id}` (confirm both items)

   1. Curl Command:
   ```
   curl -X GET 'http://localhost:8000/users/1/logs/3' \
     -H 'access_token: tusk'
   ```

   2. Result:
   ```
   {"category":"Breakfast","month":1,"day":1,"year":2021,"time":"08:30:00","items":[{"name":"Johnny's Family Omelette","calories":450.0,"protein":35.0,"carbs":20.0,"fat":15.0},{"name":"Super Healthy Sausage","calories":450.0,"protein":30.0,"carbs":20.0,"fat":20.0}]}
   ```

---

# Flow 3: Meal Plan

## Scenario:
Jolyne has been using DataFit for the first time today, and wants to see what her day's meals look like overall.

## Steps:
- Jolyne logs a meal item using `POST /users/{user_id}/items`:
```
{
  "name": "Johnny's Family Omelette",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```

- She creates a log for Monday's Breakfast using `POST /users/{user_id}/logs`:
```
{
  "month": 5,
  "day": 11,
  "year": 2026,
  "time": "09:30",
  "category": "Breakfast"
}
```

- She links the item to the log using `POST /users/{user_id}/logs/{log_id}/items`:
```
{
  "item_ids": [3213]
}
```

- She retrieves all food logged for that entry using `GET /users/{user_id}/logs/{log_id}`:
```
{
  "category": "Breakfast",
  "month": 5,
  "day": 11,
  "year": 2026,
  "time": "09:30:00",
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

---

# Test Results

## Flow 3
Tested locally against `http://localhost:8000` with API key `tusk`.

1. `POST /users/{user_id}/items`

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"name": "Johnny'\''s Family Omelette", "calories": 450, "protein": 35, "carbs": 20, "fat": 15}'
   ```

   2. Result:
   ```
   {"item_id":7,"user_id":1,"status":"created"}
   ```

2. `POST /users/{user_id}/logs` (create Breakfast log)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/logs' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"month": 5, "day": 11, "year": 2026, "time": "09:30", "category": "Breakfast"}'
   ```

   2. Result:
   ```
   {"log_id":4}
   ```

3. `POST /users/{user_id}/logs/{log_id}/items` (link omelette to log)

   1. Curl Command:
   ```
   curl -X POST 'http://localhost:8000/users/1/logs/4/items' \
     -H 'access_token: tusk' \
     -H 'Content-Type: application/json' \
     -d '{"item_ids": [7]}'
   ```

   2. Result:
   ```
   {"status":"items added"}
   ```

4. `GET /users/{user_id}/logs/{log_id}` (retrieve full log)

   1. Curl Command:
   ```
   curl -X GET 'http://localhost:8000/users/1/logs/4' \
     -H 'access_token: tusk'
   ```

   2. Result:
   ```
   {"category":"Breakfast","month":5,"day":11,"year":2026,"time":"09:30:00","items":[{"name":"Johnny's Family Omelette","calories":450.0,"protein":35.0,"carbs":20.0,"fat":15.0}]}
   ```
