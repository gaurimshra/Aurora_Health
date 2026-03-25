def women_health_logic(data):
    phase = (data.get("cycle_phase") or "").lower()
    pregnant = data.get("pregnant")
    postpartum = data.get("postpartum")

    if pregnant:
        trimester = data.get("pregnancy_trimester") or "unknown"
        return (
            f"Pregnancy support: use clinician-approved training, prioritize hydration, moderate movement, "
            f"and symptom-aware recovery. Current trimester logged: {trimester}."
        )
    if postpartum:
        weeks = data.get("postpartum_weeks") or "unknown"
        return (
            f"Postpartum support: rebuild gradually with breathing, walking, pelvic floor awareness, "
            f"and progressive strength as recovery allows. Postpartum weeks logged: {weeks}."
        )

    if phase == "menstrual":
        return "Do light yoga, walking, and stretching. Avoid intense workouts."
    if phase == "ovulation":
        return "Energy may be higher. This is a good phase for strength training."
    if phase == "follicular":
        return "Progressive strength work and moderate cardio usually fit well here."
    if phase == "luteal":
        return "Lower intensity slightly and prioritize recovery, sleep, and hydration."
    return "Moderate activity recommended."
