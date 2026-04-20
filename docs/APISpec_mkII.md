# API Specification for Data-Fit

## 1. User Profiles

### 1.1. New Profile - `/profiles/` (POST)

Create a new profile for a user. Profiles will store information about user fitness measurements.

**Request**:

```json
[
  {
    "profile_name": "string",
    "age": "number",
    "weight": "number",
    "height": "number"
  }
]
```

**Response**:

```json
[
  {
    "profile_id": "string"
  }
]
```

## 2. User Agendas

### 2.1: New User Agenda - `/agendas/` (POST)

Create a new list of goals, called an agenda, to be tracked for a user. Agenda will initially be empty.

**Request**:

```json
[
  {
    "profile_id": "string"
  }
]
```

**Response**:

```json
[
  {
    "agenda_id": "string"
  }
]
```

### 2.2: Add Goal to User Agenda - `/agendas/{agenda_id}/goals/{goal_id}` (PUT)

Add a newly created goal to a user's agenda.

**Request**:

```json
[
  {
    "nutrient_name": "string",
    "nutrient_quantity": "number",
    "nutrient_unit": "string",
    "nutrient_frequency": "number",
    "nutrient_freq_unit": "string"
  }
]
```

**Response**:

```json
[
  {
    "success": "boolean"
  }
]
```

### 2.3: Retrieve User Goal - `/goals/search` (GET)

Get a goal from a user's agenda.

**Query Parameters**:

- `profile_id` (required): id for the user's profile
- `nutrient_name` (optional): name of the nutrient in the user's goal

**Response**:

JSON object with nutrient information will be returned:

- `nutrient_name`: The name of the found nutrient
- `nutrient_quantity`: The quantity of the nutrient needed to fulfill the goal
- `nutrient_unit`: The measurement unit for the nutrient (g, mg, etc.)
- `nutrient_frequency`: The frequency at which the goal needs to be met
- `nutrient_freq_unit`: The measurement unit for the nutrient frequency (day, week, etc.)
