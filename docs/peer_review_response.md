# Peer Review Feedback

## Flow 1 Testing (Victor Wu)

There wasn't really an issue in the code since the endpoint
for this flow successfully returns the id for the user and
an error if the user's email already exists. The command that
we supplied was a might've been incorrectly formatted, so that
was most likely the issue, but that's been resolved, and
the correct output should be returning now.

### Example Flow 1: Profile editing and creation

Curl command:

```
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
Just make sure to replace the `***` where it says
`'access_token: ***'` with the actual api key.

If the user doesn't exist yet:
```
{"user_id":2}
```

If user does exist:
```
{"detail":"User with this email already exists."}
```

---


