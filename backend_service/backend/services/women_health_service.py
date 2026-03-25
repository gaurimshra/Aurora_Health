import json
from datetime import UTC, datetime

from backend.agents.cycle_agent import analyze_cycle
from backend.models.health import SymptomInsight
from sqlalchemy import select

from backend.services.db import PeriodLog, get_session
from backend.services.memory_service import remember
from backend.services.profile_service import get_user_profile


def _validate_period_dates(start_date: str, end_date: str) -> None:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if end < start:
        raise ValueError("end_date must be the same day or after start_date")


def log_period_entry(user_id: str, entry: dict) -> dict:
    _validate_period_dates(entry["start_date"], entry["end_date"])
    payload = dict(entry)
    payload["user_id"] = user_id

    with get_session() as session:
        session.add(
            PeriodLog(
                user_id=user_id,
                log_json=json.dumps(payload),
                start_date=payload["start_date"],
                created_at=datetime.now(UTC),
            )
        )
        session.commit()
    remember(
        user_id,
        "period-log",
        (
            f"Period log from {payload['start_date']} to {payload['end_date']} with symptoms "
            f"{', '.join(payload.get('symptoms', [])) or 'none'} and mood {payload.get('mood', 'stable')}."
        ),
        {"flow_level": payload.get("flow_level"), "symptoms": payload.get("symptoms", [])},
    )
    return payload


def _get_period_logs(user_id: str) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(PeriodLog)
            .where(PeriodLog.user_id == user_id)
            .order_by(PeriodLog.start_date.asc(), PeriodLog.id.asc())
        ).all()
    return [json.loads(row.log_json) for row in rows]


def _build_concerns(profile: dict | None, period_logs: list[dict], cycle_data: dict) -> list[dict]:
    concerns: list[dict] = []
    symptoms = {symptom.lower() for log in period_logs[-3:] for symptom in log.get("symptoms", [])}

    if cycle_data["irregularity_score"] in {"moderate", "high"}:
        concerns.append(
            SymptomInsight(
                flag="cycle-variation",
                detail="Cycle timing varies noticeably. Track for longer and consider clinical guidance if this persists.",
            ).model_dump()
        )
    if "fatigue" in symptoms or "dizziness" in symptoms:
        concerns.append(
            SymptomInsight(
                flag="energy-low",
                detail="Low energy symptoms may align with recovery, iron intake, sleep, or workload issues.",
            ).model_dump()
        )
    if "acne" in symptoms or "mood swings" in symptoms:
        concerns.append(
            SymptomInsight(
                flag="hormone-pattern",
                detail="Repeated skin or mood symptoms can reflect hormonal shifts. This app is not diagnostic.",
            ).model_dump()
        )
    if profile:
        for concern in profile.get("hormonal_concerns", []):
            concerns.append(
                SymptomInsight(
                    flag="profile-concern",
                    detail=f"Profile concern logged: {concern}. Keep monitoring with a clinician if symptoms are ongoing.",
                ).model_dump()
            )
    return concerns[:4]


def _nutrition_focus(profile: dict | None, period_logs: list[dict]) -> list[str]:
    symptoms = {symptom.lower() for log in period_logs[-3:] for symptom in log.get("symptoms", [])}
    focus = [
        "Prioritize protein at each meal to support recovery and hormone health.",
        "Keep hydration steady and include fruits and vegetables daily.",
    ]
    if "fatigue" in symptoms:
        focus.append("Discuss iron-rich foods with your diet plan, such as lentils, beans, spinach, and lean proteins.")
    if "cramps" in symptoms:
        focus.append("Magnesium-rich foods like nuts, seeds, and leafy greens may support comfort.")
    if profile and profile.get("pregnant"):
        focus.append("Pregnancy needs individual clinical guidance. Focus on regular meals, hydration, and prenatal support.")
    if profile and profile.get("postpartum"):
        focus.append("Postpartum recovery often benefits from higher protein, fluids, and convenient nutrient-dense snacks.")
    return focus[:4]


def _workout_focus(profile: dict | None, cycle_data: dict) -> list[str]:
    phase = cycle_data["predicted_phase"]
    focus = ["Match training intensity to energy, sleep, and stress rather than pushing every day."]
    if phase == "menstrual":
        focus.append("Favor walking, mobility, light strength, and lower-intensity sessions if symptoms are present.")
    elif phase == "follicular":
        focus.append("Progressive strength and skill work often fit well during higher-energy days.")
    elif phase == "ovulation-window":
        focus.append("Use energy peaks for confident strength sessions while protecting recovery.")
    else:
        focus.append("In the luteal phase, reduce volume slightly if sleep, cravings, or recovery feel harder.")
    if profile and profile.get("pregnant"):
        trimester = profile.get("pregnancy_trimester") or "unknown"
        focus.append(f"Pregnancy-safe training should be clinician-approved. Current profile trimester: {trimester}.")
    if profile and profile.get("postpartum"):
        focus.append("Postpartum training should rebuild gradually with core, breathing, walking, and pelvic floor awareness.")
    return focus[:4]


def get_women_health_dashboard(user_id: str) -> dict:
    period_logs = _get_period_logs(user_id)
    profile = get_user_profile(user_id)
    cycle_data = analyze_cycle(period_logs)
    return {
        "user_id": user_id,
        "average_cycle_length": cycle_data["average_cycle_length"],
        "average_period_length": cycle_data["average_period_length"],
        "next_period_start": cycle_data["next_period_start"],
        "predicted_phase": cycle_data["predicted_phase"],
        "irregularity_score": cycle_data["irregularity_score"],
        "recent_logs": period_logs[-6:],
        "possible_concerns": _build_concerns(profile, period_logs, cycle_data),
        "nutrition_focus": _nutrition_focus(profile, period_logs),
        "workout_focus": _workout_focus(profile, cycle_data),
        "disclaimer": (
            "This is a wellness tracking feature, not a medical diagnosis. "
            "Persistent irregularity, missed periods, severe pain, pregnancy concerns, or hormonal symptoms need clinician review."
        ),
    }
