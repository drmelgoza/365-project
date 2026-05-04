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
Joseph is has just begun using DataFit, and has just finished his breakfast for the day.
To keep up with his protein goal, he must now add the meal into the DataFit meal log.

### Steps:
- using his userid, Joseph calls POST `users/4032/meal-logs` with the following info:
```
{
  "name": "Johnny's Family Omelette",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```
- Joseph then recieves the following output:
```
{
  "mealId": "m101",
  "userId": "4032",
  "status": "created"
}
```
- Joseph wants to ensure the meal is considered a breakfast meal, so he calls `/users/4032/meals/m101/category` with the following info:
```
{
  "category":"Lunch"
}
```
- Finally, Joseph recieves the following output:
```
{
  "mealId": "m101",
  "category": "Lunch",
  "status": "updated"
}
```


## Flow 3: Meal Tracking

### Scenario:
Jolyne has been using DataFit for the first time today, and wants to see what her day's meals look like overall.

### Steps:
- Jolyne calls the following endpoint using her userId, `/users/12345/meals` resulting in:
```
{
  "userId": "12345",
  "meals": [
    {
      "mealId": "m2",
      "name": "Grilled Chicken Salad",
      "category": "Lunch",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15,
      "time": "2026-04-20T12:30:00Z"
    },
    {
      "mealId": "m1",
      "name": "Oatmeal with Berries",
      "category": "Breakfast",
      "calories": 300,
      "protein": 10,
      "carbs": 50,
      "fat": 5,
      "time": "2026-04-20T08:00:00Z"
    }
  ]
}
```
