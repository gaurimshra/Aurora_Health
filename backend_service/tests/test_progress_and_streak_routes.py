def test_streak_checkin_and_fetch(client, auth_headers):
    first = client.post(
        "/streaks/check-in",
        json={
            "date": "2026-03-18",
            "workout_completed": True,
            "nutrition_completed": False,
            "journal_note": "started",
        },
        headers=auth_headers,
    )
    second = client.post(
        "/streaks/check-in",
        json={
            "date": "2026-03-19",
            "workout_completed": True,
            "nutrition_completed": True,
            "journal_note": "kept going",
        },
        headers=auth_headers,
    )
    summary = client.get("/streaks/me", headers=auth_headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["current_streak"] == 2
    assert summary.status_code == 200
    assert summary.json()["longest_streak"] == 2


def test_progress_log_summary_and_coach(client, auth_headers):
    log_one = client.post(
        "/progress/log",
        json={
            "date": "2026-03-18",
            "weight": 70,
            "energy_level": 5,
            "mood": "steady",
            "workout_minutes": 20,
            "adherence_score": 5,
            "notes": "hard day",
        },
        headers=auth_headers,
    )
    log_two = client.post(
        "/progress/log",
        json={
            "date": "2026-03-19",
            "weight": 69.5,
            "energy_level": 7,
            "mood": "motivated",
            "workout_minutes": 40,
            "adherence_score": 8,
            "notes": "better energy",
        },
        headers=auth_headers,
    )
    summary = client.get("/progress/me", headers=auth_headers)
    coach = client.post(
        "/progress/coach",
        json={"message": "How do I stay consistent this week?"},
        headers=auth_headers,
    )

    assert log_one.status_code == 200
    assert log_two.status_code == 200
    assert summary.status_code == 200
    assert summary.json()["entries"] == 2
    assert summary.json()["trend"] == "improving-energy"
    assert len(summary.json()["history"]) == 2
    assert coach.status_code == 200
    assert coach.json()["reply"]
    assert coach.json()["next_steps"]


def test_tracking_history_and_memory_search(client, auth_headers):
    workout = client.post(
        "/tracking/workout",
        json={
            "date": "2026-03-18",
            "workout_type": "strength",
            "duration_minutes": 45,
            "intensity": "moderate",
            "completed": True,
            "notes": "Focused on lower body strength",
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
            "notes": "Good hydration and enough protein",
        },
        headers=auth_headers,
    )
    history = client.get("/tracking/history", headers=auth_headers)
    memory_search = client.post(
        "/tracking/memory-search",
        json={"query": "strength workout protein", "top_k": 3},
        headers=auth_headers,
    )

    assert workout.status_code == 200
    assert diet.status_code == 200
    assert history.status_code == 200
    assert len(history.json()["recent_memories"]) >= 2
    assert memory_search.status_code == 200
    assert memory_search.json()["query"] == "strength workout protein"
    assert memory_search.json()["results"]
