# Summary on Meal Flow

This flow is used when a user wants to review their meal information in the app. The user first retrieves their logged meals, then views the meal categories those entries fall under, and finally checks overall meal statistics. This helps the user understand their eating habits and track nutrition over time.

## Flow Order

1. Get Meals
2. Get Categories
3. Get Meal Stats

## 1. Get Meals (GET)

**Endpoint:** `/users/{userId}/meals`

### Description

This endpoint is called when the user wants to see the meals they have logged.

### Input

```
GET /users/12345/meals
```

### Output

```json
{
  "userId":"12345",
  "meals": [
    {
      "mealId":"m1",
      "name":"Grilled Chicken Salad",
      "category":"Lunch",
      "calories":450,
      "protein":35,
      "carbs":20,
      "fat":15,
      "time":"2026-04-20T12:30:00Z"
    },
    {
      "mealId":"m2",
      "name":"Oatmeal with Berries",
      "category":"Breakfast",
      "calories":300,
      "protein":10,
      "carbs":50,
      "fat":5,
      "time":"2026-04-20T08:00:00Z"
    }
  ]
}
```

---

## 2. Get Categories (GET)

**Endpoint:** `/users/{userId}/categories`

### Description

After viewing their meals, the user can retrieve the meal categories associated with those logged meals.

### Input

```
GET /users/12345/categories
```

### Output

```json
{
  "userId":"12345",
  "categories": [
    {
      "name":"Breakfast",
      "mealCount":10
    },
    {
      "name":"Lunch",
      "mealCount":8
    },
    {
      "name":"Dinner",
      "mealCount":7
    },
    {
      "name":"Snack",
      "mealCount":5
    }
  ]
}
```

---

## 3. Get Meal Stats (GET)

**Endpoint:** `/users/{userId}/meal-stats`

### Description

Finally, the user retrieves summary statistics about their meals, such as total meals logged, calories consumed, and their most frequent meal category.

### Input

```
GET /users/12345/meal-stats
```

### Output

```json
{
  "userId":"12345",
  "stats": {
    "totalMeals":30,
    "averageCaloriesPerMeal":420,
    "totalCalories":12600,
    "macros": {
      "protein":900,
      "carbs":1500,
      "fat":400
    },
    "mostFrequentCategory":"Lunch"
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

---

## 1. Create Meal Log (POST)

The user submits basic meal details (name and nutritional information).

The system creates a new meal record and returns a unique meal ID to identify it.

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

---

## 2. Assign Category to Meal (PUT)

The user assigns a category (e.g., breakfast, lunch, dinner) to the created meal.

The system updates the meal with the selected category and confirms the change.

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

---

## 3. Update Meal Time (PUT)

The user records the time the meal was consumed.

The system updates the meal with the provided timestamp and confirms the update.

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