import pytest
from datetime import date
from app import app as flask_app
from models import db, Exercise, Workout, WorkoutExercise

# Fixtures
@pytest.fixture(scope="function")
def app():
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove(); db.drop_all()

@pytest.fixture
def client(app): return app.test_client()

@pytest.fixture
def seed_ids(app):
    # Returns plain IDs — avoids DetachedInstanceError between fixture/test
    e1 = Exercise(name="Bench Press", category="Strength", equipment_needed=True)
    e2 = Exercise(name="Plank",       category="Endurance",equipment_needed=False)
    w1 = Workout(date=date(2025,4,14), duration_minutes=60)
    db.session.add_all([e1, e2, w1]); db.session.commit()
    we = WorkoutExercise(workout_id=w1.id, exercise_id=e1.id, reps=10, sets=4)
    db.session.add(we); db.session.commit()
    return {"eids":[e1.id,e2.id], "wids":[w1.id], "weids":[we.id]}

# Sample test classes
class TestGetWorkouts:
    def test_returns_200(self, client, seed_ids):
        assert client.get("/workouts").status_code == 200
    def test_returns_all(self, client, seed_ids):
        assert len(client.get("/workouts").get_json()) == 1

class TestCreateWorkout:
    def test_201_on_valid(self, client, seed_ids):
        r = client.post("/workouts", json={"date":"2025-05-01","duration_minutes":45})
        assert r.status_code == 201
    def test_422_zero_duration(self, client, seed_ids):
        r = client.post("/workouts", json={"date":"2025-05-01","duration_minutes":0})
        assert r.status_code == 422

class TestDeleteWorkout:
    def test_204_and_cascade(self, client, app, seed_ids):
        wid = seed_ids["wids"][0]
        assert client.delete(f"/workouts/{wid}").status_code == 204
        with app.app_context():
            assert WorkoutExercise.query.filter_by(workout_id=wid).count() == 0

class TestModelValidations:
    def test_blank_name_raises(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="cannot be empty"):
                Exercise(name="  ", category="Strength")
    def test_bad_category_raises(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Category must be one of"):
                Exercise(name="Curl", category="Yoga")