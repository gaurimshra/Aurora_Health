def test_full_endpoint_smoke_flow(client):
    register_payload = {
        "name": "Endpoint User",
        "username": "endpoint_user",
        "email": "endpoint_user@example.com",
        "password": "Password123!",
    }

    register = client.post("/auth/register", json=register_payload)
    assert register.status_code in {200, 400}

    login = client.post(
        "/auth/login",
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login.status_code == 200
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "name": "Endpoint User",
        "age": 28,
        "gender": "female",
        "weight": 62.5,
        "height_cm": 165,
        "goal": "build strength",
        "level": "intermediate",
        "pregnant": False,
        "postpartum": False,
        "hormonal_concerns": ["pcos"],
        "dietary_restrictions": [],
        "lifestyle": {
            "sleep_hours": 7.5,
            "water_liters": 2.4,
            "stress_level": 4,
            "activity_level": "moderate",
            "dietary_preference": "balanced",
            "health_goals": ["strength", "energy"],
        },
    }

    responses = {
        "auth_me": client.get("/auth/me", headers=headers),
        "profile_post": client.post("/profile", json=profile_payload, headers=headers),
        "profile_me": client.get("/profile/me", headers=headers),
        "progress_log": client.post(
            "/progress/log",
            json={
                "energy_level": 7,
                "mood": "good",
                "workout_minutes": 35,
                "adherence_score": 8,
                "notes": "ok",
            },
            headers=headers,
        ),
        "progress_me": client.get("/progress/me", headers=headers),
        "progress_coach": client.post(
            "/progress/coach",
            json={"message": "How am I doing?"},
            headers=headers,
        ),
        "tracking_workout": client.post(
            "/tracking/workout",
            json={
                "workout_type": "strength",
                "duration_minutes": 40,
                "intensity": "moderate",
                "completed": True,
                "notes": "solid",
            },
            headers=headers,
        ),
        "tracking_diet": client.post(
            "/tracking/diet",
            json={
                "meals_followed": 3,
                "hydration_liters": 2.2,
                "protein_grams": 110,
                "cravings": ["sweet"],
                "notes": "fine",
            },
            headers=headers,
        ),
        "tracking_feedback": client.post(
            "/tracking/feedback",
            json={"category": "ui", "feedback": "nice", "rating": 8},
            headers=headers,
        ),
        "tracking_history": client.get("/tracking/history", headers=headers),
        "tracking_memory_search": client.post(
            "/tracking/memory-search",
            json={"query": "strength", "top_k": 3},
            headers=headers,
        ),
        "tracking_weekly_report": client.get("/tracking/weekly-report", headers=headers),
        "streaks_check_in": client.post(
            "/streaks/check-in",
            json={
                "workout_completed": True,
                "nutrition_completed": False,
                "journal_note": "done",
            },
            headers=headers,
        ),
        "streaks_me": client.get("/streaks/me", headers=headers),
        "women_health_log_period": client.post(
            "/women-health/log-period",
            json={
                "start_date": "2026-03-01",
                "end_date": "2026-03-05",
                "symptoms": ["fatigue", "cramps"],
                "flow_level": "moderate",
                "mood": "low",
                "cravings": ["chocolate"],
                "notes": "tracking",
            },
            headers=headers,
        ),
        "women_health_dashboard": client.get("/women-health/dashboard", headers=headers),
        "chat": client.post("/chat", json={"message": "Hello coach"}),
        "generate_plan": client.post(
            "/generate-plan",
            json=profile_payload,
        ),
    }

    failures = {
        name: {"status": response.status_code, "body": response.text}
        for name, response in responses.items()
        if response.status_code != 200
    }
    assert failures == {}
