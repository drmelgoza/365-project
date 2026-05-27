# Peer Review Feedback

> [!IMPORTANT] 
> All new test cases in the [v3_manual_test_results.md](https://github.com/drmelgoza/365-project/blob/main/test/v3_manual_test_results.md) file

## New Test Case #1 (Victor Wu): Updating User Stats

***Feedback:***
New test case was implemented and seems to be working correctly. We thought the test was good to implement to
test that a user's stats were updating correctly.

## New Test Case #2 (Victor Wu): Basic Flow Test

***Feedback:*** This test case seems to be working correctly and is a good test case to test
that a majority of endpoints work as intended.

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