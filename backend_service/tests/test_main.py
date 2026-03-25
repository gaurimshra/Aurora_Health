from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_home_route_returns_ok():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Aurora AI Backend Running"}
