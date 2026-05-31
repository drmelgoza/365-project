# Peer Review Feedback

> [!IMPORTANT] 
> All new test cases in the [v3_manual_test_results.md](https://github.com/drmelgoza/365-project/blob/main/test/v3_manual_test_results.md) file

# Revisions for feedback from Victor Wu (Issues 1-4):

## New Test Case #1: Updating User Stats

***Feedback:***
New test case was implemented and seems to be working correctly. We thought the test was good to implement to
test that a user's stats were updating correctly.

## New Test Case #2: Basic Flow Test

***Feedback:*** This test case seems to be working correctly and is a good test case to test
that a majority of endpoints work as intended.

## Schema/API Design Changes:
1. Meal Log dates are now recorded in a single ISO-date column called `date` in the `user_logs` table.
2. Meal plans and Meal logs now implement quantities. The macronutrient counts in the `user_items` table are considered to be for a single serving, and serving size can be adjusted when adding the item to a meal log or meal plan.
3. Constraints are now placed on numeric values (user health info, food item macronutrient info). Date and email values are properly constrained, and macronutrient and plan types only use a set of acceptable values.
4. (Insert here when plans are updated)
5. (Insert here when plans are updated)
6. Meal Log management is now completely nested under the same prefix `users/{user_id}/logs`.
7. The endpoint `GET users/{user_id}/items` has been added to allow users to view their personal list of food items.
8. All user owned resources (food_items, goals, logs and plans) are all now located under the endpoint prefix `users/{user_id}`. As suggested, this shows that these resources are directly tied to a user.
9. Users can now be deleted using `DELETE /users/{user_id}` and items can now be deleted using `DELETE users/{user_id}`.
10. Food items can now be edited with `PATCH /users/{user_id}/items/{item_id}`, and (insert here when plans are updated)
11. User log history can now be retrieved with `GET /users/{user_id}/logs`. This endpoint functions as a search page, allowing multiple optional search parameters, such as meal category, date, and the log_id.
12. The FastAPI website sections are now organized by resource. For consistency, all sections are organized in `POST`, `GET`, `PATCH`, `DELETE` order, with some endpoint types being omitted as needed.
---

## New Test Case #1 (Iris Aeron): Negative Nutrition Values

**_Feedback:_** We modified our code to now check for negative values, so this test was good to implement in order to
prevent any negative values from being logged into the database.

## New Test Case #2 (Iris Aeron): Invalid Meal Log Date

**_Feedback:_** This test case was implemented and was a good test case to implement because it helped
test invalid input for the date section when creating a meal log.

## New Test Case #3 (Iris Aeron): Duplicate Item in the Same Log

**_Feedback:_** We chose not to implement duplicate prevention because allowing repeated item IDs can reasonably
represent multiple servings of the same food item within a single meal log.

---

## New Test Case #1 (Sumedha Kundurthi): Invalid Time

**_Feedback:_** This test case is similar to a previous test case, so it was omitted.

## New Test Case #2 (Sumedha Kundurthi): Delete non-existent item

**_Feedback:_** We implemented this test case because checking whether an item exists before deletion helps prevent
invalid operations from being performed on non-existent entries in the database.