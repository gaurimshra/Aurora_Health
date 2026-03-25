def test_tracking_history_and_weekly_report(client, auth_headers):
    workout = client.post(
        "/tracking/workout",
        json={
            "date": "2026-03-18",
            "workout_type": "strength",
            "duration_minutes": 45,
            "intensity": "moderate",
            "completed": True,
            "notes": "legs",
        },
        headers=auth_headers,
    )
    diet = client.post(
        "/tracking/diet",
        json={
            "date": "2026-03-18",
            "meals_followed": 3,
            "hydration_liters": 2.5,
            "protein_grams": 95,
            "cravings": ["sweet"],
            "notes": "good day",
        },
        headers=auth_headers,
    )
    feedback = client.post(
        "/tracking/feedback",
        json={"category": "coach", "feedback": "The plan felt realistic", "rating": 8},
        headers=auth_headers,
    )
    history = client.get("/tracking/history", headers=auth_headers)
    weekly = client.get("/tracking/weekly-report", headers=auth_headers)

    assert workout.status_code == 200
    assert diet.status_code == 200
    assert feedback.status_code == 200
    assert history.status_code == 200
    assert len(history.json()["workout_logs"]) == 1
    assert len(history.json()["diet_logs"]) == 1
    assert history.json()["recent_memories"]
    assert weekly.status_code == 200
    assert weekly.json()["summary"]
