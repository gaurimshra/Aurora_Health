def build_progress_reply(profile: dict | None, recent_logs: list[dict], message: str) -> dict:
    latest = recent_logs[-1] if recent_logs else {}
    goal = profile.get("goal", "health") if profile else "health"
    level = profile.get("level", "beginner") if profile else "beginner"

    insights: list[str] = []
    next_steps: list[str] = []

    if latest:
        insights.append(
            f"Latest check-in shows energy {latest.get('energy_level', 'n/a')}/10 and "
            f"{latest.get('workout_minutes', 0)} workout minutes."
        )
        if latest.get("adherence_score", 0) <= 5:
            insights.append("Consistency looks lower right now, so recovery and smaller daily targets may help.")
            next_steps.append("Aim for one non-negotiable 20-minute workout tomorrow.")
        else:
            insights.append("Adherence is solid, which is a strong base for steady progress.")
            next_steps.append("Maintain the same training rhythm for the next 5 to 7 days.")
    else:
        insights.append("No progress logs yet, so the first priority is building a baseline.")
        next_steps.append("Log one check-in today with energy, mood, and workout minutes.")

    next_steps.append(f"Keep your {goal} plan realistic for your current {level} level.")
    next_steps.append("Review sleep, hydration, and protein intake before increasing training load.")

    reply = (
        f"Progress coach: {message.strip()} "
        f"Based on your recent data, stay focused on sustainable progress rather than perfect days."
    )
    return {"reply": reply, "insights": insights, "next_steps": next_steps[:3]}
