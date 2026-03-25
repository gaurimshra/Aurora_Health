from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_generate_plan_returns_json():
    payload = {
        "goal": "fat loss",
        "level": "beginner",
        "weight": 72,
        "gender": "female",
        "cycle_phase": "ovulation",
    }

    response = client.post("/generate-plan", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert set(body.keys()) == {"workout", "diet", "women_health"}
    assert isinstance(body["workout"], str)
    assert isinstance(body["diet"], str)
    assert isinstance(body["women_health"], str)


def test_generate_plan_validates_payload():
    payload = {
        "goal": "fat loss",
        "level": "beginner",
        "gender": "female",
    }

    response = client.post("/generate-plan", json=payload)

    assert response.status_code == 422
