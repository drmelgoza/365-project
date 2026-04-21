# 3 Example User Flows

## Flow 1: Profile Creation

### Scenario:
Jonathan is a new user to DataFit, and wants to begin using the app
to prepare for his martial arts tournament. To begin tracking his goals,
he will first start by creating a profile.

### Steps:
- go to `/profiles` to begin a new profile and retrieve the new profileid `1234`
- then, go to `/profiles/1234` to view his profile and ensure its created

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
