# Workout Tracker API

A RESTful backend API for a workout tracking application used by personal trainers. Built with Flask, SQLAlchemy, and Marshmallow, this API allows trainers to manage workouts and exercises, assign exercises to workouts with specific performance data (reps, sets, duration), and track training sessions over time.

---

## Table of Contents

- [Project Description](#project-description)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Relationships](#relationships)
- [Validations](#validations)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Git Workflow](#git-workflow)

---

## Project Description

This API serves as the backend for a workout tracking application. Personal trainers can use it to:

- Create and manage **workouts** (date, duration, notes)
- Create and manage reusable **exercises** (name, category, equipment)
- **Assign exercises to workouts** with performance details like reps, sets, and duration
- Retrieve workouts with their full exercise breakdown
- Retrieve exercises with all the workouts they appear in

The application enforces data integrity at three levels: database table constraints, SQLAlchemy model validations, and Marshmallow schema validations.

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.8.13+ | Core language |
| Flask | 2.2.2 | Web framework |
| Flask-SQLAlchemy | 3.0.3 | ORM — database interaction |
| Flask-Migrate | 3.1.0 | Database migrations |
| Marshmallow | 3.20.1 | Serialization and validation |
| Werkzeug | 2.2.2 | WSGI utilities |
| SQLite | built-in | Database |
| Pipenv | latest | Virtual environment |

---

## Project Structure

```
workout-tracker-api/
├── .gitignore
├── Pipfile
├── Pipfile.lock
├── README.md
└── server/
    ├── app.py          # Flask app, configuration, all API endpoints
    ├── models.py       # SQLAlchemy models, relationships, model validations
    ├── schemas.py      # Marshmallow schemas, schema validations
    ├── seed.py         # Database seed file
    ├── instance/
    │   └── app.db      # SQLite database (auto-generated)
    └── migrations/     # Flask-Migrate migration files
        ├── env.py
        ├── alembic.ini
        └── versions/
```

---

## Data Models

### Exercise
Represents a reusable exercise that can be added to many workouts.

| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Required, unique |
| category | String(50) | Required |
| equipment_needed | Boolean | Default: False |

Valid categories: `Strength`, `Cardio`, `Flexibility`, `Balance`, `Endurance`

---

### Workout
Represents a single training session.

| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary key |
| date | Date | Required |
| duration_minutes | Integer | Required, must be > 0 |
| notes | Text | Optional |

---

### WorkoutExercise (Join Table)
Links exercises to workouts and stores performance data for that session.

| Column | Type | Constraints |
|---|---|---|
| id | Integer | Primary key |
| workout_id | Integer | Foreign key → workouts.id |
| exercise_id | Integer | Foreign key → exercises.id |
| reps | Integer | Optional, must be > 0 if provided |
| sets | Integer | Optional, must be > 0 if provided |
| duration_seconds | Integer | Optional, must be > 0 if provided |

---

## Relationships

```
Workout ──────────────── WorkoutExercise ──────────────── Exercise
  │                            │                              │
  │   has many WorkoutExercises│                              │
  │                            │ belongs to Workout           │
  │                            │ belongs to Exercise          │
  │                            │                              │
  └── has many Exercises ──────┘─── has many Workouts ───────┘
      (through WorkoutExercise)      (through WorkoutExercise)
```

- A **Workout** has many **WorkoutExercises**
- An **Exercise** has many **WorkoutExercises**
- A **WorkoutExercise** belongs to a **Workout**
- A **WorkoutExercise** belongs to an **Exercise**
- A **Workout** has many **Exercises** through **WorkoutExercises**
- An **Exercise** has many **Workouts** through **WorkoutExercises**

Deleting a Workout or Exercise automatically deletes its associated WorkoutExercise records (cascade delete).

---

## Validations

Three layers of validation protect data integrity.

### Table Constraints (database level)
Enforced by SQLite — the database will reject bad data even outside the app.

| Table | Constraint |
|---|---|
| workouts | duration_minutes must be > 0 |
| workout_exercises | reps must be NULL or > 0 |
| workout_exercises | sets must be NULL or > 0 |
| workout_exercises | duration_seconds must be NULL or > 0 |
| exercises | name must be unique |

### Model Validations (SQLAlchemy level)
Enforced by Python before data hits the database.

| Model | Field | Rule |
|---|---|---|
| Exercise | name | Cannot be blank or whitespace |
| Exercise | category | Must be one of the 5 valid categories |
| Workout | duration_minutes | Must be a positive integer |
| WorkoutExercise | reps | Must be positive if provided |
| WorkoutExercise | sets | Must be positive if provided |

### Schema Validations (Marshmallow level)
Enforced on incoming request data before it reaches the models.

| Schema | Field | Rule |
|---|---|---|
| WorkoutSchema | duration_minutes | Minimum value of 1 |
| WorkoutSchema | notes | Maximum 500 characters |
| ExerciseSchema | name | Length between 1 and 100 characters |
| ExerciseSchema | category | Must be one of 5 valid options |
| WorkoutExerciseSchema | reps | Must be positive if provided |
| WorkoutExerciseSchema | sets | Must be positive if provided |
| WorkoutExerciseSchema | duration_seconds | Must be positive if provided |

---

## Installation

### Prerequisites
- Python 3.8.13 or higher
- Git
- Pipenv (`pip install pipenv`)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Caleb125-source/workout-tracker-api.git
cd workout-tracker-api
```

**2. Install dependencies**
```bash
pipenv install
```

**3. Activate the virtual environment**
```bash
pipenv shell
```

**4. Navigate to the server directory**
```bash
cd server
```

**5. Initialise the database**
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade head
```

**6. Seed the database with sample data**
```bash
python seed.py
```

Expected output:
```
Seeded: 7 exercises, 3 workouts, 6 links
```

---

## Running the App

From inside the `server/` directory:

```bash
flask run -p 5555
```

The API will be available at:
```
http://localhost:5555
```

To stop the server press `Ctrl + C`.

To re-seed the database at any time (resets all data):
```bash
python seed.py
```

---

## API Endpoints

### Workouts

#### GET /workouts
Returns a list of all workouts.

```bash
curl -s http://localhost:5555/workouts | python -m json.tool
```

Response `200`:
```json
[
  {
    "id": 1,
    "date": "2025-04-14",
    "duration_minutes": 60,
    "notes": "Upper body day"
  }
]
```

---

#### GET /workouts/\<id\>
Returns a single workout with its full exercise breakdown including reps, sets, and duration.

```bash
curl -s http://localhost:5555/workouts/1 | python -m json.tool
```

Response `200`:
```json
{
  "id": 1,
  "date": "2025-04-14",
  "duration_minutes": 60,
  "notes": "Upper body day",
  "workout_exercises": [
    {
      "id": 1,
      "exercise_id": 1,
      "reps": 10,
      "sets": 4,
      "duration_seconds": null,
      "exercise": {
        "id": 1,
        "name": "Bench Press",
        "category": "Strength",
        "equipment_needed": true
      }
    }
  ]
}
```

Response `404` if not found:
```json
{ "error": "Workout not found." }
```

---

#### POST /workouts
Creates a new workout.

```bash
curl -s -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-05-01","duration_minutes":45,"notes":"Leg day"}' \
  | python -m json.tool
```

Request body:
| Field | Type | Required |
|---|---|---|
| date | string (YYYY-MM-DD) | Yes |
| duration_minutes | integer | Yes |
| notes | string | No |

Response `201` on success.
Response `422` on validation failure:
```json
{ "errors": { "duration_minutes": ["Duration must be at least 1 minute."] } }
```

---

#### DELETE /workouts/\<id\>
Deletes a workout and all its associated WorkoutExercise records.

```bash
curl -s -X DELETE http://localhost:5555/workouts/1 -o /dev/null -w "%{http_code}"
```

Response `204` on success (empty body).
Response `404` if not found.

---

### Exercises

#### GET /exercises
Returns a list of all exercises.

```bash
curl -s http://localhost:5555/exercises | python -m json.tool
```

Response `200`:
```json
[
  {
    "id": 1,
    "name": "Bench Press",
    "category": "Strength",
    "equipment_needed": true
  }
]
```

---

#### GET /exercises/\<id\>
Returns a single exercise with all the workouts it has been used in.

```bash
curl -s http://localhost:5555/exercises/1 | python -m json.tool
```

Response `200`:
```json
{
  "id": 1,
  "name": "Bench Press",
  "category": "Strength",
  "equipment_needed": true,
  "workout_exercises": [
    {
      "id": 1,
      "workout_id": 1,
      "reps": 10,
      "sets": 4,
      "duration_seconds": null,
      "workout": {
        "id": 1,
        "date": "2025-04-14",
        "duration_minutes": 60,
        "notes": "Upper body day"
      }
    }
  ]
}
```

Response `404` if not found.

---

#### POST /exercises
Creates a new exercise.

```bash
curl -s -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name":"Pull Up","category":"Strength","equipment_needed":false}' \
  | python -m json.tool
```

Request body:
| Field | Type | Required | Valid values |
|---|---|---|---|
| name | string | Yes | Any, max 100 chars |
| category | string | Yes | Strength, Cardio, Flexibility, Balance, Endurance |
| equipment_needed | boolean | No | true / false (default: false) |

Response `201` on success.
Response `422` on validation failure:
```json
{ "errors": { "category": ["Must be one of: Strength, Cardio, Flexibility, Balance, Endurance."] } }
```

---

#### DELETE /exercises/\<id\>
Deletes an exercise and all its associated WorkoutExercise records.

```bash
curl -s -X DELETE http://localhost:5555/exercises/1 -o /dev/null -w "%{http_code}"
```

Response `204` on success.
Response `404` if not found.

---

### WorkoutExercises

#### POST /workouts/\<workout_id\>/exercises/\<exercise_id\>/workout_exercises
Adds an exercise to a workout with optional performance data.

```bash
curl -s -X POST http://localhost:5555/workouts/2/exercises/3/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps":12,"sets":3}' \
  | python -m json.tool
```

Request body (all optional):
| Field | Type | Rule |
|---|---|---|
| reps | integer | Must be > 0 if provided |
| sets | integer | Must be > 0 if provided |
| duration_seconds | integer | Must be > 0 if provided |

Response `201` on success:
```json
{
  "id": 7,
  "workout_id": 2,
  "exercise_id": 3,
  "reps": 12,
  "sets": 3,
  "duration_seconds": null,
  "exercise": { "id": 3, "name": "Plank", "category": "Endurance" },
  "workout": { "id": 2, "date": "2025-04-15", "duration_minutes": 45 }
}
```

Response `404` if workout or exercise not found.
Response `422` on validation failure.

---

## Testing

### Run the automated test suite

```bash
cd server
python -m pytest tests.py -v
```

Expected output:
```
collected 55 items

tests.py::TestGetWorkouts::test_returns_200          PASSED
tests.py::TestGetWorkout::test_includes_workout_exercises PASSED
tests.py::TestCreateWorkout::test_201_on_success     PASSED
tests.py::TestCreateWorkout::test_422_zero_duration  PASSED
tests.py::TestDeleteWorkout::test_cascade_deletes    PASSED
tests.py::TestModelValidations::test_blank_name      PASSED
...

55 passed in 5.99s
```

### Manual testing with curl

Start the server in one terminal:
```bash
flask run -p 5555
```

Run curl commands from a second terminal. See the [API Endpoints](#api-endpoints) section above for the full list of curl examples including validation failure cases.

---

## Git Workflow

This project was built using a feature branch workflow. Each feature was developed on its own branch and merged back to `main` after completion.

| Branch | What was built |
|---|---|
| `main` | Initial scaffold — README, Pipfile, .gitignore |
| `feature/models` | Exercise, Workout, WorkoutExercise models with relationships, table constraints, and model validations |
| `feature/database-setup` | Flask app skeleton, flask db init/migrate/upgrade, seed file |
| `feature/schemas` | Marshmallow schemas with schema validations |
| `feature/endpoints` | All 9 REST endpoints with serialization and error handling |
