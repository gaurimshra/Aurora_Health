import json
from datetime import UTC, date, datetime

from sqlalchemy import select

from backend.services.agentic_ai_service import generate_coach_response
from backend.services.db import ProgressLog, get_session
from backend.services.memory_service import remember, search_memories, get_recent_memories
from backend.services.profile_service import get_user_profile


def _fetch_logs(user_id: str) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(ProgressLog)
            .where(ProgressLog.user_id == user_id)
            .order_by(ProgressLog.log_date.asc(), ProgressLog.id.asc())
        ).all()
    return [json.loads(row.entry_json) for row in rows]


def log_progress(user_id: str, entry: dict) -> dict:
    payload = dict(entry)
    payload["user_id"] = user_id
    payload["date"] = payload.get("date") or date.today().isoformat()
    with get_session() as session:
        session.add(
            ProgressLog(
                user_id=user_id,
                log_date=payload["date"],
                entry_json=json.dumps(payload),
                created_at=datetime.now(UTC),
            )
        )
        session.commit()
    remember(
        user_id,
        "progress-log",
        (
            f"Progress log on {payload['date']}: energy {payload.get('energy_level')}/10, "
            f"mood {payload.get('mood')}, workout {payload.get('workout_minutes')} minutes, "
            f"adherence {payload.get('adherence_score')}/10. Notes: {payload.get('notes', '')}"
        ),
        {"date": payload["date"], "energy_level": payload.get("energy_level")},
    )
    return payload


def get_progress_summary(user_id: str) -> dict:
    logs = _fetch_logs(user_id)
    latest = logs[-1] if logs else None
    trend = "no-data"
    if len(logs) >= 2:
        if logs[-1]["energy_level"] > logs[0]["energy_level"]:
            trend = "improving-energy"
        elif logs[-1]["energy_level"] < logs[0]["energy_level"]:
            trend = "declining-energy"
        else:
            trend = "steady"
    return {
        "user_id": user_id,
        "entries": len(logs),
        "latest": latest,
        "trend": trend,
        "history": logs[-20:],
    }


def progress_coach(user_id: str, message: str) -> dict:
    logs = _fetch_logs(user_id)
    profile = get_user_profile(user_id)
    memory_hits = search_memories(user_id, message, top_k=5)
    remember(user_id, "coach-message", f"User asked Aurora: {message}", {"source": "coach"})
    return generate_coach_response(profile, logs[-5:], memory_hits, message)


def get_recent_progress_memories(user_id: str, limit: int = 10) -> list[dict]:
    return get_recent_memories(user_id, limit=limit)
