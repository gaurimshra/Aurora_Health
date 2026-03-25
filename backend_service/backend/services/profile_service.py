import json
from datetime import UTC, datetime

from backend.agents.health_insight_agent import build_profile_summary
from backend.services.db import UserProfile, get_session
from backend.services.memory_service import remember


def save_user_profile(user_id: str, profile: dict) -> dict:
    payload = dict(profile)
    payload["user_id"] = user_id
    serialized = json.dumps(payload)

    with get_session() as session:
        existing = session.get(UserProfile, user_id)
        if existing:
            existing.profile_json = serialized
            existing.updated_at = datetime.now(UTC)
        else:
            session.add(
                UserProfile(
                    user_id=user_id,
                    profile_json=serialized,
                    updated_at=datetime.now(UTC),
                )
            )
        session.commit()

    remember(
        user_id,
        "profile",
        build_profile_summary(payload),
        {"goal": payload.get("goal"), "level": payload.get("level")},
    )
    return {
        "user_id": user_id,
        "saved": True,
        "summary": build_profile_summary(payload),
        "profile": payload,
    }


def get_user_profile(user_id: str) -> dict | None:
    with get_session() as session:
        row = session.get(UserProfile, user_id)

    if row is None:
        return None
    return json.loads(row.profile_json)
