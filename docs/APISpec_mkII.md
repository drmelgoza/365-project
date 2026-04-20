# API Specification for Data-Fit

### 1. Profiles


## 1.1 Create Profile
POST /profiles
Create a new user profile.
Request
{
  "profile_name": "John",
  "age": 25,
  "weight": 70,
  "height": 175
}
Response
{
  "profile_id": "p123"
}


## 1.2 Get Profile
GET /profiles/{profile_id}
Retrieve profile information.
Response
{
  "profile_id": "p123",
  "profile_name": "John",
  "age": 25,
  "weight": 70,
  "height": 175
}
### 2. Agendas


## 2.1 Create Agenda
POST /agendas
Create a new agenda for a user.
Request
{
  "profile_id": "p123"
}
Response
{
  "agenda_id": "a456"
}


## 2.2 Add Goal to Agenda
PUT /agendas/{agenda_id}/goals
Add a goal to the agenda.
Request
{
  "nutrient_name": "protein",
  "nutrient_quantity": 100,
  "nutrient_unit": "g",
  "nutrient_frequency": 1,
  "nutrient_freq_unit": "day"
}
Response
{
  "success": true
}


## 2.3 Get Goals for Agenda
GET /agendas/{agenda_id}/goals
Retrieve all goals in a user’s agenda.
Response
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
### 3. Goals


## 3.1 Create Goal
POST /goals
Create a goal independently (can later be added to an agenda).
Request
{
  "nutrient_name": "fiber",
  "nutrient_quantity": 30,
  "nutrient_unit": "g",
  "nutrient_frequency": 1,
  "nutrient_freq_unit": "day"
}
Response
{
  "goal_id": "g789"
}


## 3.2 Delete Goal
DELETE /goals/{goal_id}
Remove a goal.
Response
{
  "success": true
}


### 4. Tracking / Stats


## 4.1 Log Meal
POST /meals
Track a meal for a profile.
Request
{
  "profile_id": "p123",
  "meal_name": "Chicken Salad",
  "calories": 400
}
Response
{
  "success": true
}

## 4.2 Get Stats
GET /profiles/{profile_id}/stats
Retrieve summary stats for a user.
Response
{
  "total_calories": 1800,
  "protein": "90g",
  "status": "under goal"
}

### 5 Example User Flows

## Flow 1: User Meeting Goals
Summary:
User checks progress and logs a status update to stay accountable.
Steps:
GET /goals
GET /status
POST /status
Example Input:
POST /status
{
  "user_id": "123",
  "steps": 8000,
  "calories_burned": 500
}
Example Output:
{
  "message": "Status updated successfully",
  "progress": "80% of daily goal"
}
Motivation:
Tracking progress helps users stay consistent and aware of their health habits.

## Flow 2: Meal Planning
Summary:
User generates a meal plan based on personal data and goals.
Steps:
GET /data
GET /goals
GET /health
POST /meal-plan
Example Input:
POST /meal-plan
{
  "user_id": "123",
  "diet": "vegetarian",
  "calorie_target": 2000
}
Example Output:
{
  "breakfast": "Oatmeal with fruits",
  "lunch": "Quinoa salad",
  "dinner": "Vegetable stir fry"
}
Motivation:
Personalized plans make it easier to stick to healthy eating habits.

## Flow 3: Meal Tracking & Summary
Summary:
User logs meals and later reviews insights.
Steps:
POST /meals
POST /time
POST /category
GET /meals
GET /stats
Example Input:
POST /meals
{
  "user_id": "123",
  "meal": "Grilled chicken salad",
  "calories": 400
}
Example Output:
{
  "total_calories": 1800,
  "protein": "120g",
  "status": "Within goal"
}
Motivation:
Logging meals increases awareness and helps users improve nutrition over time.
