# Peer Review Feedback

> [!IMPORTANT] 
> All new test cases in the [v3_manual_test_results.md](https://github.com/drmelgoza/365-project/blob/main/test/v3_manual_test_results.md) file

---
# Revisions for Victor Wu's Feedback (Issues 1-4):

## New Test Case #1: Updating User Stats

***Feedback:***
New test case was implemented and seems to be working correctly. We thought the test was good to implement to
test that a user's stats were updating correctly.

## New Test Case #2: Basic Flow Test

***Feedback:*** This test case seems to be working correctly and is a good test case to test
that a majority of endpoints work as intended.

## Schema/API Design Changes:
1. Meal Log dates are now recorded in a single date column called `date` in the `user_logs` table.
2. Meal plans and Meal logs now implement quantities. The macronutrient counts in the `user_items` table are considered to be for a single serving, and serving size can be adjusted when adding the item to a meal log or meal plan.
3. Constraints are now placed on numeric values (user health info, food item macronutrient info). Date and email values are properly constrained, and macronutrient and plan types only use a set of acceptable values.
4. Meal plans now support multiple plans per user instead of only returning a single hidden plan.
5. Meal plan routes are now nested under `users/{user_id}/plans`, making ownership clearer and showing that plans belong to users.
6. Meal Log management is now completely nested under the same prefix `users/{user_id}/logs`.
7. The endpoint `GET users/{user_id}/items` has been added to allow users to view their personal list of food items.
8. All user owned resources (food_items, goals, logs and plans) are all now located under the endpoint prefix `users/{user_id}`. As suggested, this shows that these resources are directly tied to a user.
9. Users can now be deleted using `DELETE /users/{user_id}` and items can now be deleted using `DELETE users/{user_id}`.
10. Food items can now be edited with `PATCH /users/{user_id}/items/{item_id}`, and meal plans can now be revised with `PATCH /users/{user_id}/plans/{plan_id}`.
11. User log history can now be retrieved with `GET /users/{user_id}/logs`. This endpoint functions as a search page, allowing multiple optional search parameters, such as meal category, date, and the log_id.
12. The FastAPI website sections are now organized by resource. For consistency, all sections are organized in `POST`, `GET`, `PATCH`, `DELETE` order, with some endpoint types being omitted as needed.
---

# Revisions for Iris Aeron's Feedback (Issues 5-8):

## New Test Case #1: Negative Nutrition Values

**_Feedback:_** We modified our code to now check for negative values, so this test was good to implement in order to
prevent any negative values from being logged into the database.

## New Test Case #2: Invalid Meal Log Date

**_Feedback:_** This test case was implemented and was a good test case to implement because it helped
test invalid input for the date section when creating a meal log.

## New Test Case #3: Duplicate Item in the Same Log

**_Feedback:_** We chose not to implement duplicate prevention because allowing repeated item IDs can reasonably
represent multiple servings of the same food item within a single meal log.

## Schema/API Design Changes:
1. `APISpec.md` and `ExampleFlows.md` have been edited to properly showcase the newest version of the API.
2. All documentation now uses the term `user(s)` to represent the user entity.
3. Macro goals have been implemented with `POST`, `GET`, `PATCH`, `DELETE` endpoints being added to manage the new resource. Now, meal logs can be aggregated by day to calculate daily macro goal progress. 
4. The meal statistics functionality has been added with `GET users/{user_id}/statstics`. This endpoint allows users to see how their meal logs for a specific day compare to the macro goals they have set.
5. Meal log dates are now recorded in a single date column called `date` in the `user_logs` table.
6. Meal log time has been removed to avoid redundancy with the already established meal categories (Breakfast, Lunch, Dinner, etc.)
7. Meal log categories have now been standardized to avoid inconsistent values that would complicate sorting and grouping. The established categories are `["breakfast", "lunch", "dinner", "snack", "supper"]` 
8. User item macronutrients now are constrained to positive integer or float values.
9. The previous get-by-day/category plan endpoints have been consolidated into user-owned plan endpoints with optional query parameters when filtering is needed.
10. User age is now set as an `integer` column.
11. Plan endpoints are now structured as `users/{user_id}/plans`, `users/{user_id}/plans/{plan_id}`, and `users/plans/{user_id}/{plan_id}/items` to make it clear that plans belong to users.
12. Users can now retrieve all of their plans with `GET /users/{user_id}/plans`.

---

# Revisions for Sumedha Kundurthi's Feedback (Issues 9-12):

## New Test Case #1: Invalid Time

**_Feedback:_** This test case is similar to a previous test case, so it was omitted.

## New Test Case #2: Delete non-existent item

**_Feedback:_** We implemented this test case because checking whether an item exists before deletion helps prevent
invalid operations from being performed on non-existent entries in the database.

## Schema/API Design Changes:
1. `APISpec.md` now references the `/users` set of endpoints,  and any references to `/agendas` have been deleted.
2. `APISpec.md` now consistently uses snake case.
3. `PATCH` endpoints are now properly referenced in `APISpec.md`
4. `PATCH` endpoints now return information about the values being changed for the specified resource.
5. `DELETE` endpoints now return the id of the resource that was deleted.
6. timestamps have been removed from the API, and all dates are now stored in one YYYY-MM-DD formatted column.
7. (Unable to address.)
8. Logs are now consistently nested under the URI prefix `users/{user_id}/logs`.
9. Plans are now retrievable through one function that combines the functionality of the two previous renditions.
10. Food items are made and stored in a personal directory using the `POST users/{user_id}/items` endpoint. They can be later referenced as part of meal logs or meal plans using other endpoints. This prevents users from having to repeat information for the same food item across multiple plans or logs.
11. Plan endpoints have now been standardized to follow a `plans/{user_id}` prefix.
12. Plans are now retrievable through `/plans/{user_id}/plan` which can either retrieve all plans in bulk or return plans given a filter request.