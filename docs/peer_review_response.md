# Peer Review Feedback

> [!NOTE]
> Document not yet finished.

> [!IMPORTANT] 
> All new test cases in the [v3_manual_test_results.md](365-project/test/v3_manual_test_results.md) file

## Flow 1 Testing (Victor Wu)

There wasn't really an issue in the code since the endpoint
for this flow successfully returns the id for the user and
an error if the user's email already exists. The command that
we supplied was a might've been incorrectly formatted, so that
was most likely the issue, but that's been resolved, and
the correct output should be returning now.

### Example Flow 1: Profile editing and creation

Curl command:

```bash
 curl -X 'POST' \
   'https://datafit-meal-tracker.onrender.com/users/' \
   -H 'accept: application/json' \
   -H 'access_token: ***' \
   -H 'Content-Type: application/json' \
   -d '{
   "username": "karate_kid_84",
   "name": "Daniel",
   "email": "daniel@somemail.com",
   "height": 68,
   "weight": 125,
   "age": 19
 }'
```
This should be the correct command (a typo was fixed).
> [!IMPORTANT]
> Make sure to replace the `***` where it says
> `'access_token: ***'` with the actual api key.

If the user doesn't exist yet:
```json
{"user_id":2}
```

If user does exist:
```json
{"detail":"User with this email already exists."}
```

## New Test Case #1 (Victor Wu)
Curl command:

```bash
curl -X POST \
 "https://datafit-meal-tracker.onrender.com/users/" \
 -H "accept: application/json" \
 -H "access_token: ***" \
 -H "Content-Type: application/json" \
 -d '{
 "username": "viciswoozy",
 "name": "Victor",
 "email": "victor@somemail.com",
 "height": 70,
 "weight": 185,
 "age": 20
}'
```

Result for creation:

```json
{"user_id":11}
```

Curl command for updating users stats:

```bash
curl -X PATCH \
  "https://datafit-meal-tracker.onrender.com/users/11" \
  -H "accept: application/json" \
  -H "access_token: ***" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 100
  }'
```

Results for updating:

```json
{"user_id":11,"status":"updated"}
```
***Feedback:***
New test case seems to be working correctly.

## New Test Case #2

***Feedback:*** This test case seems to be working correctly and is a good test case to test
that a majority of endpoints work as intended.

---

## Test Case #3 (Iris Aeron)

