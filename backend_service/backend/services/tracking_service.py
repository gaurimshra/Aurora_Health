import json
from datetime import UTC, date, datetime, timedelta

from backend.core.openai_client import generate_text
from sqlalchemy import select

from backend.services.db import DietLog, PeriodLog, ProgressLog, WorkoutLog, get_session
from backend.services.memory_service import get_recent_memories, remember, search_memories
from backend.services.progress_service import get_progress_summary
from backend.services.profile_service import get_user_profile
from backend.services.streak_service import get_streak
from backend.services.women_health_service import get_women_health_dashboard


def _utcnow() -> str:
    return datetime.now(UTC)


def _log_generic(table_name: str, user_id: str, log_date: str, entry: dict) -> dict:
    model_map = {
        "workout_logs": WorkoutLog,
        "diet_logs": DietLog,
    }
    model = model_map[table_name]
    with get_session() as session:
        session.add(
            model(
                user_id=user_id,
                log_date=log_date,
                entry_json=json.dumps(entry),
                created_at=_utcnow(),
            )
        )
        session.commit()
    return entry


def log_workout(user_id: str, entry: dict) -> dict:
    payload = dict(entry)
    payload["date"] = payload.get("date") or date.today().isoformat()
    payload["user_id"] = user_id
    saved = _log_generic("workout_logs", user_id, payload["date"], payload)
    remember(
        user_id,
        "workout-log",
        (
            f"Workout on {payload['date']}: {payload.get('workout_type')} for "
            f"{payload.get('duration_minutes')} minutes at {payload.get('intensity')} intensity. "
            f"Completed: {payload.get('completed')}. Notes: {payload.get('notes', '')}"
        ),
        {"date": payload["date"], "workout_type": payload.get("workout_type")},
    )
    return saved


def log_diet(user_id: str, entry: dict) -> dict:
    payload = dict(entry)
    payload["date"] = payload.get("date") or date.today().isoformat()
    payload["user_id"] = user_id
    saved = _log_generic("diet_logs", user_id, payload["date"], payload)
    remember(
        user_id,
        "diet-log",
        (
            f"Diet log on {payload['date']}: meals followed {payload.get('meals_followed')}, "
            f"hydration {payload.get('hydration_liters')} liters, protein {payload.get('protein_grams')} grams, "
            f"cravings {', '.join(payload.get('cravings', [])) or 'none'}. Notes: {payload.get('notes', '')}"
        ),
        {"date": payload["date"], "protein_grams": payload.get("protein_grams")},
    )
    return saved


def save_feedback(user_id: str, category: str, feedback: str, rating: int | None) -> dict:
    remember(
        user_id,
        "feedback",
        f"Feedback on {category}: {feedback}",
        {"category": category, "rating": rating},
    )
    return {"saved": True, "category": category, "rating": rating}


def _fetch_table_history(table_name: str, user_id: str) -> list[dict]:
    model_map = {
        "workout_logs": WorkoutLog,
        "diet_logs": DietLog,
        "progress_logs": ProgressLog,
    }
    model = model_map[table_name]
    with get_session() as session:
        rows = session.scalars(
            select(model)
            .where(model.user_id == user_id)
            .order_by(model.log_date.desc(), model.id.desc())
            .limit(50)
        ).all()
    return [json.loads(row.entry_json) for row in rows]


def get_history(user_id: str) -> dict:
    with get_session() as session:
        period_rows = session.scalars(
            select(PeriodLog)
            .where(PeriodLog.user_id == user_id)
            .order_by(PeriodLog.start_date.desc(), PeriodLog.id.desc())
            .limit(50)
        ).all()
    return {
        "workout_logs": _fetch_table_history("workout_logs", user_id),
        "diet_logs": _fetch_table_history("diet_logs", user_id),
        "progress_logs": _fetch_table_history("progress_logs", user_id),
        "period_logs": [json.loads(row.log_json) for row in period_rows],
        "recent_memories": get_recent_memories(user_id, limit=10),
    }


def generate_weekly_report(user_id: str) -> dict:
    today = date.today()
    week_start = (today - timedelta(days=6)).isoformat()
    week_end = today.isoformat()
    profile = get_user_profile(user_id) or {}
    progress = get_progress_summary(user_id)
    streak = get_streak(user_id)
    women = get_women_health_dashboard(user_id)
    history = get_history(user_id)
    memory_hits = search_memories(user_id, "weekly report progress wins struggles patterns", top_k=6)

    wins = []
    risks = []
    recommendations = []

    if progress["entries"] > 0:
        wins.append(f"You logged {progress['entries']} progress check-ins.")
    if streak["current_streak"] >= 3:
        wins.append(f"Current streak is {streak['current_streak']} days.")
    if women.get("predicted_phase") not in {"insufficient-data", "unknown"}:
        wins.append(f"Cycle-aware context is available for the current phase: {women.get('predicted_phase')}.")

    latest = progress.get("latest") or {}
    if latest and latest.get("energy_level", 0) <= 4:
        risks.append("Energy has been low recently.")
    if latest and latest.get("adherence_score", 10) <= 5:
        risks.append("Adherence is inconsistent, so the plan may be too ambitious.")
    if women.get("irregularity_score") in {"moderate", "high"}:
        risks.append("Cycle timing looks variable. Keep tracking and consider clinical guidance if this persists.")

    recommendations.extend(
        [
            f"Keep your {profile.get('goal', 'health')} plan realistic for your current routine.",
            "Use workout, diet, and progress logging at least 3 times this week to improve Aurora's recommendations.",
            "Protect sleep and hydration before increasing training intensity.",
        ]
    )

    memory_context = "\n".join(f"- {item.get('content')}" for item in memory_hits) or "- No memory yet"
    summary_prompt = f"""
    You are Aurora, an adaptive AI health coach.
    User goal: {profile.get('goal', 'health')}
    Current streak: {streak.get('current_streak', 0)}
    Progress trend: {progress.get('trend', 'no-data')}
    Weekly wins: {wins}
    Weekly risks: {risks}
    Memory context:
    {memory_context}
    Write a concise weekly report summary for the user.
    """
    summary = generate_text(
        summary_prompt,
        fallback="This week shows useful tracking progress. Keep building consistency and adjust intensity to your recovery.",
    )
    return {
        "user_id": user_id,
        "period_start": week_start,
        "period_end": week_end,
        "summary": summary,
        "wins": wins,
        "risks": risks,
        "recommendations": recommendations[:3],
    }
