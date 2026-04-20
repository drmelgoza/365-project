# Summary on Meal

This flow allows users to view their logged meals, meal categories, and overall meal statistics. It helps users understand their eating habits and track nutritional trends over time.

## 1. Get Meals

**Endpoint:** `/users/{userId}/meals`

Return a list of meals that have been logged by a user

```json
{
  "userId": "12345",
  "meals": [
    {
      "mealId": "m1",
      "name": "Grilled Chicken Salad",
      "category": "Lunch",
      "calories": 450,
      "protein": 35,
      "carbs": 20,
      "fat": 15,
      "time": "2026-04-20T12:30:00Z"
    },
    {
      "mealId": "m2",
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

## 2. Get Categories

**Endpoint:**  `/users/{userId}/categories`

Returns the meal categories associated with the user’s logged meals

**Response:**

```json
{
  "userId": "12345",
  "categories": [
    {
      "name": "Breakfast",
      "mealCount": 10
    },
    {
      "name": "Lunch",
      "mealCount": 8
    },
    {
      "name": "Dinner",
      "mealCount": 7
    },
    {
      "name": "Snack",
      "mealCount": 5
    }
  ]
}
```

## 3. Get Meal Stats

**Endpoint:** `/users/{userId}/meal-stats`

Returns summary statistics about the user’s meals, such as total meals, calories, and most frequent category

**Response:**

```json
{
  "userId": "12345",
  "stats": {
    "totalMeals": 30,
    "averageCaloriesPerMeal": 420,
    "totalCalories": 12600,
    "macros": {
      "protein": 900,
      "carbs": 1500,
      "fat": 400
    },
    "mostFrequentCategory": "Lunch"
  }
}
```
---

# Meal Tracking (Log a Meal) Flow

This flow is used when a user logs a new meal into the system. The user submits meal details, assigns a category, and records the time. This allows the system to store structured meal data for tracking and analysis.

## Flow Order

1. Create Meal Log
2. Assign Category to Meal
3. Update Meal Time

## 1. Create Meal Log (POST)

**Endpoint:** `/users/{userId}/meal-logs`

### Input

```json
{
  "name":"Grilled Chicken Salad",
  "calories":450,
  "protein":35,
  "carbs":20,
  "fat":15
}
```

### Output

```json
{
  "mealId":"m101",
  "userId":"12345",
  "status":"created"
}
``` 

## 2. Assign Category to Meal (PUT)

**Endpoint:** `/users/{userId}/meals/{mealId}/category`

### Input

```
{
  "category":"Lunch"
}
```

### Output

```json
{
  "mealId":"m101",
  "category":"Lunch",
  "status":"updated"
}
```

## 3. Update Meal Time (PUT)

**Endpoint:** `/users/{userId}/meals/{mealId}/time`

### Input

```json
{
  "time":"2026-04-20T12:30:00Z"
}
```

### Output

```json
{
  "mealId":"m101",
  "time":"2026-04-20T12:30:00Z",
  "status":"updated"
}
```