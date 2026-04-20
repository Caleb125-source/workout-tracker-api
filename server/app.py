from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (exercise_schema, exercises_schema, workout_schema, workouts_schema, workout_exercise_schema) # type: ignore

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)

# Routes added in feature/endpoints
# Workouts
@app.get("/workouts")
def get_workouts():
    return make_response(workouts_schema.dump(Workout.query.all()), 200)

@app.get("/workouts/<int:id>")
def get_workout(id):
    w = db.session.get(Workout, id)
    if not w: return make_response({"error":"Workout not found."}, 404)
    return make_response(workout_schema.dump(w), 200)

@app.post("/workouts")
def create_workout():
    try:
        data = workout_schema.load(request.get_json())
    except ValidationError as e:
        return make_response({"errors": e.messages}, 422)
    try:
        w = Workout(**data); db.session.add(w); db.session.commit()
    except ValueError as e:
        db.session.rollback(); return make_response({"error": str(e)}, 422)
    return make_response(workout_schema.dump(w), 201)

@app.delete("/workouts/<int:id>")
def delete_workout(id):
    w = db.session.get(Workout, id)
    if not w: return make_response({"error":"Workout not found."}, 404)
    db.session.delete(w); db.session.commit()
    return make_response("", 204)

# Exercises
@app.get("/exercises")
def get_exercises():
    return make_response(exercises_schema.dump(Exercise.query.all()), 200)

@app.get("/exercises/<int:id>")
def get_exercise(id):
    e = db.session.get(Exercise, id)
    if not e: return make_response({"error":"Exercise not found."}, 404)
    return make_response(exercise_schema.dump(e), 200)

@app.post("/exercises")
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json())
    except ValidationError as e:
        return make_response({"errors": e.messages}, 422)
    try:
        ex = Exercise(**data); db.session.add(ex); db.session.commit()
    except (ValueError, Exception) as e:
        db.session.rollback(); return make_response({"error": str(e)}, 422)
    return make_response(exercise_schema.dump(ex), 201)

@app.delete("/exercises/<int:id>")
def delete_exercise(id):
    e = db.session.get(Exercise, id)
    if not e: return make_response({"error":"Exercise not found."}, 404)
    db.session.delete(e); db.session.commit()
    return make_response("", 204)

# WorkoutExercise (join) 
@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    if not db.session.get(Workout,  workout_id):
        return make_response({"error":"Workout not found."},  404)
    if not db.session.get(Exercise, exercise_id):
        return make_response({"error":"Exercise not found."}, 404)
    payload = {**(request.get_json() or {}),
               "workout_id": workout_id, "exercise_id": exercise_id}
    try:
        data = workout_exercise_schema.load(payload)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 422)
    try:
        we = WorkoutExercise(**data); db.session.add(we); db.session.commit()
    except ValueError as e:
        db.session.rollback(); return make_response({"error": str(e)}, 422)
    return make_response(workout_exercise_schema.dump(we), 201)

if __name__ == "__main__":
    app.run(port=5555, debug=True)