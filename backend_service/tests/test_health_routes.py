def test_profile_and_women_health_flow(client, auth_headers):
    profile_payload = {
        "name": "Asha",
        "age": 29,
        "gender": "female",
        "weight": 58,
        "height_cm": 162,
        "goal": "general fitness",
        "level": "beginner",
        "pregnant": False,
        "postpartum": False,
        "pregnancy_trimester": None,
        "postpartum_weeks": None,
        "hormonal_concerns": ["fatigue"],
        "dietary_restrictions": ["vegetarian"],
        "lifestyle": {
            "sleep_hours": 7,
            "water_liters": 2.2,
            "stress_level": 5,
            "activity_level": "moderate",
            "dietary_preference": "balanced",
            "health_goals": ["better energy", "cycle support"],
        },
    }

    response = client.post("/profile", json=profile_payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["saved"] is True

    period_one = {
        "start_date": "2026-01-01",
        "end_date": "2026-01-05",
        "symptoms": ["fatigue", "cramps"],
        "flow_level": "moderate",
        "mood": "low",
        "cravings": ["sweet"],
        "notes": "cycle one",
    }
    period_two = {
        "start_date": "2026-01-30",
        "end_date": "2026-02-03",
        "symptoms": ["acne"],
        "flow_level": "light",
        "mood": "stable",
        "cravings": [],
        "notes": "cycle two",
    }

    assert client.post("/women-health/log-period", json=period_one, headers=auth_headers).status_code == 200
    assert client.post("/women-health/log-period", json=period_two, headers=auth_headers).status_code == 200

    dashboard = client.get("/women-health/dashboard", headers=auth_headers)
    body = dashboard.json()

    assert dashboard.status_code == 200
    assert body["average_cycle_length"] == 29
    assert body["average_period_length"] == 5
    assert body["predicted_phase"] in {"menstrual", "follicular", "ovulation-window", "luteal"}
    assert len(body["recent_logs"]) == 2
    assert body["possible_concerns"]


def test_period_log_rejects_invalid_date_order(client, auth_headers):
    response = client.post(
        "/women-health/log-period",
        json={
            "start_date": "2026-03-10",
            "end_date": "2026-03-08",
            "symptoms": [],
            "flow_level": "light",
            "mood": "stable",
            "cravings": [],
            "notes": "",
        },
        headers=auth_headers,
    )

    assert response.status_code == 400
