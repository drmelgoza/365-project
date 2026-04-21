# API Specification for Data-Fit

# 1. Profiles

Profiles allow users to begin using the app by creating a profile of health information.
The health statistics can be used to help users make decisions about their meals
and determine health goals.

## Flow Order

1. Create Profile
2. Get Profile

## 1.1 Create Profile (POST)

### Endpoint: `/profiles`

Create a new user profile.

### Request

```json
[
  {
    "profile_name": "John",
    "age": 25,
    "weight": 70,
    "height": 175
  }
]
```

### Response

```json
{
  "profile_id": "p123"
}
```

## 1.2 Get Profile (GET)

### Endpoint: `/profiles/{profile_id}`

Retrieve profile information.

### Response

```json
{
  "profile_id": "p123",
  "profile_name": "John",
  "age": 25,
  "weight": 70,
  "height": 175
}
```

# 2. Agendas

Agendas are created as an organized list of goals for the user.
Users will use agenda goals to determine if the meals they are tracking are
benefitting their health goals.

## Flow Order

1. Create Agenda
2. Add Agenda Goal
3. Get Agenda Goals
4. Delete Agenda Goals (as needed)

## 2.1 Create Agenda (POST)

### Endpoint: `/agendas`

Create a new agenda for a user.

### Request

```json
{
  "profile_id": "p123"
}
```

### Response

```json
{
  "agenda_id": "a456"
}
```

## 2.2 Add Goal to Agenda (PUT)

### Endpoint: `/agendas/{agenda_id}/goals`

Add a goal to the agenda.

### Request

```json
{
  "nutrient_name": "protein",
  "nutrient_quantity": 100,
  "nutrient_unit": "g",
  "nutrient_frequency": 1,
  "nutrient_freq_unit": "day"
}
```

### Response

```json
{
  "success": true
}
```

## 2.3 Get Goals for Agenda (GET)

### Endpoint: `/agendas/{agenda_id}/goals`

Retrieve all goals in a user’s agenda.

### Response

```json
{
  "goals": [
    {
      "nutrient_name": "protein",
      "nutrient_quantity": 100,
      "nutrient_unit": "g",
      "nutrient_frequency": 1,
      "nutrient_freq_unit": "day"
    }
  ]
}
```

## 2.4 Delete Goal from Agenda (DELETE)

### Endpoint: `/agendas/{agenda_id}/goals/{goal_id}`

Remove a goal from a users agenda.

### Response

```json
{
  "success": true
}
```

# 3. Meal Logging

This set of endpoints is used when a user logs a new meal into the system. The user submits meal details, assigns a category, and records the time. This allows the system to store structured meal data for tracking and analysis.

## Flow Order

1. Create Meal Log
2. Assign Category to Meal
3. Update Meal Time

## 3.1 Create Meal Log (POST)

**Endpoint:** `/users/{userId}/meal-logs`

The user submits basic meal details (name and nutritional information).
The system creates a new meal record and returns a unique meal ID to identify it.

### Input

```json
{
  "name": "Grilled Chicken Salad",
  "calories": 450,
  "protein": 35,
  "carbs": 20,
  "fat": 15
}
```

### Output

```json
{
  "mealId": "m101",
  "userId": "12345",
  "status": "created"
}
```

## 3.2 Assign Category to Meal (PUT)

**Endpoint:** `/users/{userId}/meals/{mealId}/category`

The user assigns a category (e.g., breakfast, lunch, dinner) to the created meal.
The system updates the meal with the selected category and confirms the change.

### Input

```
{
  "category":"Lunch"
}
```

### Output

```json
{
  "mealId": "m101",
  "category": "Lunch",
  "status": "updated"
}
```

## 3.3 Update Meal Time (PUT)

**Endpoint:** `/users/{userId}/meals/{mealId}/time`

The user records the time the meal was consumed.
The system updates the meal with the provided timestamp and confirms the update.

### Input

```json
{
  "time": "2026-04-20T12:30:00Z"
}
```

### Output

```json
{
  "mealId": "m101",
  "time": "2026-04-20T12:30:00Z",
  "status": "updated"
}
```

# 4. Meals Tracking

This set of endpoints is used when a user wants to review their meal information in the app. The user first retrieves their logged meals, then views the meal categories those entries fall under, and finally checks overall meal statistics. This helps the user understand their eating habits and track nutrition over time.

## Flow Order

1. Get Meals
2. Get Categories
3. Get Meal Stats

## 4.1 Get Meals (GET)

**Endpoint:** `/users/{userId}/meals`

This endpoint is called when the user wants to see the meals they have logged.

### Input

```
GET /users/12345/meals
```

### Output

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

## 4.2 Get Categories (GET)

**Endpoint:** `/users/{userId}/categories`

After viewing their meals, the user can retrieve the meal categories associated with those logged meals.

### Input

```
GET /users/12345/categories
```

### Output

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

## 4.3 Get Meal Stats (GET)

**Endpoint:** `/users/{userId}/meal-stats`

Finally, the user retrieves summary statistics about their meals, such as total meals logged, calories consumed, and their most frequent meal category.

### Input

```
GET /users/12345/meal-stats
```

### Output

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
