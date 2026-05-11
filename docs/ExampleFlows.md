# 3 Example User Flows

## Flow 1: Profile Creation and Editing

### Scenario:
Daniel is a new user to DataFit, and wants to begin using the app
to prepare for his karate tournament. To begin tracking his goals,
he will first start by creating a profile.

### Steps:
- Danial calls `POST /users` to begin a new profile.
- With that call, he inputs the following information:
    
```
{
    "username": karate_kid_84
    "name": Daniel
    "email": daniel@somemail.com
    "height": 68
    weight: 125
    age: 19
}
```
- After the call is successfully executed, he is returned a user id; `"user_id": 20`
- Daniel now realizes after creating his profile that he's actually 5'10", so he will now call `PATCH users/20` to fix his mistake.
- With that call, he inputs the following:

```
{
    "height": 70
}
```
- Daniel is then returned the following:

```
{
    "user_id": 20,
    "status": updated
}
```
- Now, Daniel can call `GET users/20` to ensure the update went through:

```
{
    "username": karate_kid_84
    "name": Daniel
    "email": daniel@somemail.com
    "height": 70
    weight: 125
    age: 19
}
```

## Flow 2: Meal Logging

### Scenario:
Joseph has just begun using DataFit, and has just finished his breakfast for the day.
To keep up with his protein goal, he must now add the meal into the DataFit meal log.

### Steps:
- Joseph wants to add his favorite breakfast omelet to track with DataFit. Joseph calls `POST /users/4567/items` to add the omelette.

```
{
  "name": "Johnny's Family Omelet",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```

- After being created the omelet's new item id is returned:
```
{
  "item_id": 1231,
  "user_id": 4567,
  "status": "created"
}
```

- Using his user id, Joseph calls `POST /users/4567/logs` to create a meal log for breakfast:
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

- Joseph links the omelet to his log using `POST logs/1/items`:
```
{
  "item_ids": [1231]
}
```

- The output received is then:
```
{
   "item_ids": [1231]
   "status": "logged"
}
```

- Joseph forgot to log the breakfast sausage that he had as a side. He creates the sausage item first with `POST /users/4567/items`:
```
{
  "name": "Super Healthy Sausage",
  "calories": 500,
  "protein": 30,
  "carbs": 20,
  "fat": 20
}
```

- He receives the new item id:
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

- Receiving the output:
```
{
   "item_ids": [3213]
   "status": "logged"
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
      "name": "Johnny's Family Omelet",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    },
    {
      "name": "Super Healthy Sausage",
      "calories": 500,
      "protein": 30,
      "carbs": 20,
      "fat": 20
    }
  ]
}
```


## Flow 3: Meal Plan

### Scenario:
Jolyne has been using DataFit for the first time today, and wants to see what her day's meals look like overall.
##add input. outputs, api endpoints
### Logging meal (input):
```{
"items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    },
]
```
### Logging category of meal (input):
```{
    "item_id": 3213,
    "day": {"Monday"},
    "category": "Breakfast",
    "time": 9:30
}
```
### Returning food log info (output):
```{
    "day": {"Monday"},
    "time" 9:30,
    "category": "Breakfast,
    items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    }]
}
```
### Categorizing based on category (output):
```{
    "category": Breakfast,
    items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    }]
}
```
### Categorizing based on day (output):
```{
    "day": {"Monday"},
    items": [
    {
      "name": "Johnny's Family Omelette",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15
    }]
}
```
#not imp but maybe by monday
### Removing user inputted meal:
Input:
```{
    "Please input meal name, id to remove: "
}
```
Output:
```{
    "item_id", "is removed from your plan!"
}
```

    
    
