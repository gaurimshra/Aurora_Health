from backend.services.ai_orchestrator import generate_full_plan


def test_generate_full_plan_includes_women_health(monkeypatch):
    monkeypatch.setattr(
        "backend.services.ai_orchestrator.generate_plan_response",
        lambda data: {
            "workout": "workout plan",
            "diet": "diet plan",
            "women_health": "women health plan",
        },
    )

    result = generate_full_plan(
        {
            "goal": "muscle gain",
            "level": "intermediate",
            "weight": 65,
            "gender": "female",
            "cycle_phase": "follicular",
        }
    )

    assert result == {
        "workout": "workout plan",
        "diet": "diet plan",
        "women_health": "women health plan",
    }


def test_generate_full_plan_skips_women_health_for_non_female(monkeypatch):
    monkeypatch.setattr(
        "backend.services.ai_orchestrator.generate_plan_response",
        lambda data: {
            "workout": "workout plan",
            "diet": "diet plan",
            "women_health": None,
        },
    )

    result = generate_full_plan(
        {
            "goal": "endurance",
            "level": "beginner",
            "weight": 70,
            "gender": "male",
        }
    )

    assert result == {
        "workout": "workout plan",
        "diet": "diet plan",
        "women_health": None,
    }
