# Example Workflow

## Profile Creation and Editing

### Scenario:
Daniel is a new user to DataFit, and wants to begin using the app
to prepare for his karate tournament. To begin tracking his goals,
he will first start by creating a profile.

### Steps:
- Danial calls `POST /users` to begin a new profile with the following information:
    
```
{
    "username": karate_kid_84
    "name": Daniel
    "email": daniel@somemail.com
    "height": 68
    "weight": 125
    "age": 19
}
```
- After the call is successfully executed, he is returned a user id; `"user_id": 20`
- Daniel now realizes after creating his profile that he's actually 5'10", so he will now call `PATCH users/20` to fix his mistake. He inputs the following:

```
{
    "height": 70
}
```
- Daniel is then returned the following:

```
{
    "user_id": 20,
    "status": updated
}
```
- Now, Daniel can call `GET users/20` to ensure the update went through:

```
{
    "username": karate_kid_84
    "name": Daniel
    "email": daniel@somemail.com
    "height": 70
    "weight": 125
    "age": 19
}
```


# Test Results

1. `POST /users`: 
   1. Curl Command: 
   
   ``` 
    curl -X 'POST' \
      'https://datafit-meal-tracker.onrender.com/users/' \
      -H 'accept: application/json' \
      -H 'access_token: *** \
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
   
   2. Result:
    ```
   {
        "user_id": 1
    }
   ```
   
2. `PATCH users/{user_id}`:

   1. Curl Command: 
   
    ```
    curl -X 'PATCH' \
      'https://datafit-meal-tracker.onrender.com/users/1' \
      -H 'accept: application/json' \
      -H 'access_token: *** ' \
      -H 'Content-Type: application/json' \
      -d '{
      "height": 70
    }'
    ```

   2. Result:

     ```
    {
    "user_id": 1,
    "status": "updated"
    }
    ```

3. `GET users/{user_id}`

    1. Curl Command:
    ```
    curl -X 'GET' \
      'https://datafit-meal-tracker.onrender.com/users/1' \
      -H 'accept: application/json' \
      -H 'access_token: *** '
    ```
   
   2. Result:

    ```
    {
      "username": "karate_kid_84",
      "name": "Daniel",
      "email": "daniel@somemail.com",
      "height": 70,
      "weight": 125,
      "age": 19
    }
    ```