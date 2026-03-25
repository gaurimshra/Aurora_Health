import shutil
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import db, storage


@pytest.fixture()
def isolated_db(monkeypatch):
    temp_dir = Path(__file__).resolve().parent / ".tmp" / uuid.uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=True)
    db_path = temp_dir / "aurora_test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(storage, "DB_PATH", db_path)
    db.reset_database_state()
    storage.initialize_database()
    try:
        yield db_path
    finally:
        db.reset_database_state()
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def client(isolated_db):
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Asha",
            "username": "asha",
            "email": "asha@example.com",
            "password": "Password123",
        },
    )
    body = response.json()
    return {"Authorization": f"Bearer {body['token']}"}
