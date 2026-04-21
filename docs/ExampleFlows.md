### 3 Example User Flows

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
