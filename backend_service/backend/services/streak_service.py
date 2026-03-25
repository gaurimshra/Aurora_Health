import json
from datetime import UTC, date, datetime

from sqlalchemy import select

from backend.services.db import StreakCheckin, get_session
from backend.services.memory_service import remember


def _today_iso() -> str:
    return date.today().isoformat()


def _motivation_for_streak(streak_days: int) -> str:
    if streak_days >= 30:
        return "Thirty days is serious consistency. Keep compounding small wins."
    if streak_days >= 7:
        return "A full week streak is a real habit. Protect it with simple daily actions."
    if streak_days >= 3:
        return "Momentum is building. Stay accountable with one action every day."
    if streak_days >= 1:
        return "The streak has started. Show up again tomorrow."
    return "Start with today. Consistency matters more than intensity."


def _fetch_checkins(user_id: str) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(StreakCheckin)
            .where(StreakCheckin.user_id == user_id)
            .order_by(StreakCheckin.checkin_date.asc(), StreakCheckin.id.asc())
        ).all()
    return [json.loads(row.entry_json) for row in rows]


def record_checkin(user_id: str, entry: dict) -> dict:
    payload = dict(entry)
    payload["user_id"] = user_id
    checkin_date = payload.get("date") or _today_iso()
    payload["date"] = checkin_date
    inserted = False

    with get_session() as session:
        existing = session.scalar(
            select(StreakCheckin).where(
                StreakCheckin.user_id == user_id,
                StreakCheckin.checkin_date == checkin_date,
            )
        )
        if not existing:
            session.add(
                StreakCheckin(
                    user_id=user_id,
                    checkin_date=checkin_date,
                    entry_json=json.dumps(payload),
                    created_at=datetime.now(UTC),
                )
            )
            session.commit()
            inserted = True

    if inserted:
        remember(
            user_id,
            "streak-checkin",
            (
                f"Daily check-in on {checkin_date}. Workout completed: {payload.get('workout_completed')}. "
                f"Nutrition completed: {payload.get('nutrition_completed')}. Note: {payload.get('journal_note', '')}"
            ),
            {"date": checkin_date},
        )

    return get_streak(user_id, repeated=existing is not None)


def get_streak(user_id: str, repeated: bool = False) -> dict:
    checkins = _fetch_checkins(user_id)
    if not checkins:
        return {
            "user_id": user_id,
            "current_streak": 0,
            "longest_streak": 0,
            "total_checkins": 0,
            "motivation": _motivation_for_streak(0),
            "last_checkin": None,
        }

    dates = [datetime.strptime(item["date"], "%Y-%m-%d").date() for item in checkins]
    current = 1
    longest = 1
    running = 1
    for previous, current_date in zip(dates, dates[1:]):
        delta = (current_date - previous).days
        if delta == 1:
            running += 1
        elif delta > 1:
            running = 1
        longest = max(longest, running)
    current = 1
    for previous, current_date in zip(reversed(dates[:-1]), reversed(dates[1:])):
        if (current_date - previous).days == 1:
            current += 1
        else:
            break
    motivation = (
        "Already checked in today. Protect the streak by repeating tomorrow."
        if repeated
        else _motivation_for_streak(current)
    )
    return {
        "user_id": user_id,
        "current_streak": current,
        "longest_streak": longest,
        "total_checkins": len(checkins),
        "motivation": motivation,
        "last_checkin": checkins[-1]["date"],
    }
