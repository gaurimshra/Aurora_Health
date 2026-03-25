from backend.core import generate_text


def generate_workout(data):
    prompt = f"""
    Create a structured weekly workout plan.
    Goal: {data.get('goal')}
    Level: {data.get('level')}
    Weight: {data.get('weight')}
    Age: {data.get('age')}
    Activity level: {data.get('activity_level')}
    Pregnant: {data.get('pregnant')}
    Postpartum: {data.get('postpartum')}
    Pregnancy trimester: {data.get('pregnancy_trimester')}
    Postpartum weeks: {data.get('postpartum_weeks')}
    Hormonal concerns: {', '.join(data.get('hormonal_concerns', []))}
    Return a 7-day plan with recovery guidance.
    """

    if data.get("pregnant"):
        fallback = (
            "Pregnancy-aware workout plan: prioritize clinician-approved walking, mobility, breathing work, "
            "light strength, posture support, and recovery. Avoid high-risk intensity and monitor symptoms."
        )
    elif data.get("postpartum"):
        fallback = (
            "Postpartum workout plan: start with walking, breathing, core reconnection, pelvic floor awareness, "
            "light strength, and gradual progression based on recovery."
        )
    else:
        fallback = (
            f"Weekly workout plan for a {data.get('level', 'beginner')} user focused on "
            f"{data.get('goal', 'general fitness')}: 3 strength days, 2 cardio days, "
            "1 mobility day, and 1 recovery day."
        )
    return generate_text(prompt=prompt, fallback=fallback)
