import math

from backend.core.openai_client import generate_json, generate_text


def _round_number(value: float | int | None, digits: int = 1) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def analyze_user_inputs(user_data: dict, recent_logs: list[dict] | None = None) -> dict:
    recent_logs = recent_logs or []
    weight = float(user_data.get("weight") or 0)
    goal = str(user_data.get("goal") or "general fitness").strip()
    level = str(user_data.get("level") or "beginner").strip()
    sleep_hours = float((user_data.get("lifestyle") or {}).get("sleep_hours") or 0)
    stress_level = int((user_data.get("lifestyle") or {}).get("stress_level") or 5)
    activity_level = (
        user_data.get("activity_level")
        or (user_data.get("lifestyle") or {}).get("activity_level")
        or "moderate"
    )
    dietary_restrictions = user_data.get("dietary_restrictions") or []
    hormonal_concerns = user_data.get("hormonal_concerns") or []
    pregnancy_state = "pregnant" if user_data.get("pregnant") else "postpartum" if user_data.get("postpartum") else "general"

    protein_multiplier = 1.6
    if any(term in goal.lower() for term in ["muscle", "strength", "build"]):
        protein_multiplier = 1.8
    if any(term in goal.lower() for term in ["fat", "loss", "lean"]):
        protein_multiplier = max(protein_multiplier, 1.7)
    if user_data.get("pregnant") or user_data.get("postpartum"):
        protein_multiplier = max(protein_multiplier, 1.8)

    protein_target = max(80, int(math.ceil(weight * protein_multiplier))) if weight > 0 else 90
    hydration_target = _round_number(max(2.0, weight * 0.033), 1) if weight > 0 else 2.5

    recovery_risk = "moderate"
    if sleep_hours and sleep_hours < 6.5 or stress_level >= 8:
        recovery_risk = "high"
    elif sleep_hours >= 7.5 and stress_level <= 5:
        recovery_risk = "low"

    latest = recent_logs[-1] if recent_logs else {}
    adherence = latest.get("adherence_score")
    energy = latest.get("energy_level")
    if isinstance(adherence, int) and adherence <= 4:
        recovery_risk = "high"
    if isinstance(energy, int) and energy <= 4:
        recovery_risk = "high"

    focus = []
    if "strength" in goal.lower() or "muscle" in goal.lower():
        focus.append("progressive strength training")
    if "fat" in goal.lower() or "loss" in goal.lower():
        focus.append("high-consistency calorie control")
    if not focus:
        focus.append("steady general fitness")
    if recovery_risk == "high":
        focus.append("recovery-first scheduling")
    if pregnancy_state != "general":
        focus.append(f"{pregnancy_state}-aware safety")

    return {
        "goal": goal,
        "level": level,
        "activity_level": str(activity_level),
        "pregnancy_state": pregnancy_state,
        "recovery_risk": recovery_risk,
        "protein_target_grams": protein_target,
        "hydration_target_liters": hydration_target,
        "dietary_restrictions": dietary_restrictions,
        "hormonal_concerns": hormonal_concerns,
        "focus": focus,
        "latest_energy": energy,
        "latest_adherence": adherence,
    }


def _fallback_workout_plan(user_data: dict, analysis: dict) -> str:
    level = analysis["level"]
    recovery = analysis["recovery_risk"]
    pregnancy_state = analysis["pregnancy_state"]
    goal = analysis["goal"]

    if pregnancy_state == "pregnant":
        return (
            "Weekly workout plan:\n"
            "Day 1: 25 to 35 minutes of walking plus 10 minutes of breathing and mobility.\n"
            "Day 2: Light full-body strength with clinician-approved loads, posture work, and long rest periods.\n"
            "Day 3: Recovery walk and gentle stretching.\n"
            "Day 4: Mobility, core connection, and balance work.\n"
            "Day 5: Low-impact cardio such as walking or cycling if comfortable.\n"
            "Day 6: Light strength or yoga-based movement.\n"
            "Day 7: Full recovery.\n"
            "Keep sessions conversational, stop for pain, dizziness, bleeding, or unusual symptoms, and clear training changes with your clinician."
        )

    if pregnancy_state == "postpartum":
        return (
            "Weekly workout plan:\n"
            "Day 1: 20 to 30 minute walk plus breathing and core reconnection.\n"
            "Day 2: Light strength focusing on posture, glutes, upper back, and controlled tempo.\n"
            "Day 3: Recovery walk and mobility.\n"
            "Day 4: Core and pelvic-floor-aware movement.\n"
            "Day 5: Low-impact cardio.\n"
            "Day 6: Light strength repeat.\n"
            "Day 7: Recovery.\n"
            "Progress slowly, avoid rushing impact or heavy loading, and align training with medical clearance and recovery status."
        )

    day_2 = "cardio intervals" if recovery != "high" else "zone-2 cardio"
    day_4 = "full-body strength" if "strength" in goal.lower() else "hypertrophy or circuit work"
    return (
        f"Weekly workout plan for a {level} user focused on {goal}:\n"
        "Day 1: Full-body strength, 45 minutes, 5 to 6 main exercises.\n"
        f"Day 2: {day_2}, 25 to 35 minutes.\n"
        "Day 3: Mobility, walking, and recovery.\n"
        f"Day 4: {day_4}, 40 to 50 minutes.\n"
        "Day 5: Steps goal plus light core work.\n"
        "Day 6: Lower-body and pull-focused strength or a mixed athletic session.\n"
        "Day 7: Full recovery.\n"
        f"Recovery note: current recovery risk looks {recovery}, so keep 1 to 2 reps in reserve and protect sleep before adding volume."
    )


def _fallback_diet_plan(user_data: dict, analysis: dict) -> str:
    restrictions = ", ".join(analysis["dietary_restrictions"]) if analysis["dietary_restrictions"] else "none"
    protein_target = analysis["protein_target_grams"]
    hydration_target = analysis["hydration_target_liters"]
    pregnancy_state = analysis["pregnancy_state"]

    base = (
        f"Diet plan:\n"
        f"Protein target: about {protein_target} g per day.\n"
        f"Hydration target: about {hydration_target} L per day.\n"
        f"Dietary restrictions: {restrictions}.\n"
        "Meal structure: 3 main meals plus 1 to 2 planned snacks.\n"
        "Each meal: lean protein, high-fiber carbs, vegetables or fruit, and a healthy fat source.\n"
        "Snack ideas: yogurt or tofu bowl, fruit with nuts, protein smoothie, eggs, roasted chickpeas, or cottage cheese.\n"
        "Habit focus: keep protein evenly spread across the day and build meals you can repeat during busy days."
    )

    if pregnancy_state == "pregnant":
        return (
            base
            + "\nPregnancy note: prioritize regular meals, hydration, iron-rich foods, and clinician-guided prenatal nutrition."
        )
    if pregnancy_state == "postpartum":
        return (
            base
            + "\nPostpartum note: prioritize easy protein, fluids, iron-rich foods, fiber, and convenient meals that support recovery."
        )
    return base


def _fallback_women_health_guidance(user_data: dict, analysis: dict) -> str | None:
    if analysis["pregnancy_state"] == "pregnant":
        return (
            "Women's health guidance: use lower-impact training, regular meals, hydration, symptom monitoring, and clinician-approved exercise progressions."
        )
    if analysis["pregnancy_state"] == "postpartum":
        return (
            "Women's health guidance: recovery quality, gradual strength progression, core reconnection, hydration, and adequate protein should lead decisions."
        )
    if user_data.get("gender") == "female" or analysis["hormonal_concerns"]:
        concern_text = ", ".join(analysis["hormonal_concerns"]) if analysis["hormonal_concerns"] else "general cycle awareness"
        return (
            "Women's health guidance: adjust training intensity to energy, sleep, and cycle symptoms. "
            f"Current concern context: {concern_text}."
        )
    return None


def generate_plan_response(user_data: dict) -> dict:
    analysis = analyze_user_inputs(user_data)
    fallback = {
        "workout": _fallback_workout_plan(user_data, analysis),
        "diet": _fallback_diet_plan(user_data, analysis),
        "women_health": _fallback_women_health_guidance(user_data, analysis),
    }
    prompt = f"""
    Analyze the user and return JSON with keys workout, diet, women_health.
    The plans must be easy to follow, specific, safe for general wellness use, and detailed enough to act on immediately.
    Use short paragraphs or line breaks inside the string values.

    User data: {user_data}
    Derived analysis: {analysis}

    Requirements:
    - workout: 7-day structure with progression and recovery notes.
    - diet: daily nutrition framework with protein, hydration, and meal examples.
    - women_health: include only if relevant, otherwise null.
    """
    response = generate_json(prompt, fallback)
    return {
        "workout": str(response.get("workout") or fallback["workout"]),
        "diet": str(response.get("diet") or fallback["diet"]),
        "women_health": response.get("women_health") if response.get("women_health") else fallback["women_health"],
    }


def generate_coach_response(profile: dict | None, recent_logs: list[dict], memory_hits: list[dict], message: str) -> dict:
    analysis = analyze_user_inputs(profile or {}, recent_logs=recent_logs)
    latest = recent_logs[-1] if recent_logs else {}

    insights = []
    if latest:
        insights.append(
            f"Your latest check-in shows energy {latest.get('energy_level', 'n/a')}/10 and adherence {latest.get('adherence_score', 'n/a')}/10."
        )
        insights.append(
            f"Recovery risk looks {analysis['recovery_risk']}, so your plan should match sleep, stress, and consistency."
        )
    else:
        insights.append("You do not have recent logs yet, so the first step is building a useful baseline.")
        insights.append("Aurora can coach much better once workout, diet, and progress data are logged.")

    next_steps = [
        "Pick one realistic workout window for tomorrow and protect it on your calendar.",
        f"Aim for roughly {analysis['protein_target_grams']} g of protein and {analysis['hydration_target_liters']} L of water today.",
        "Keep the next 7 days repeatable instead of chasing a perfect reset.",
    ]

    fallback = {
        "reply": (
            "Here is the simplest way to move forward: lower the friction, keep the plan realistic, "
            "and repeat the same small wins until consistency feels automatic."
        ),
        "insights": insights[:2],
        "next_steps": next_steps[:3],
    }

    prompt = f"""
    Return JSON with keys reply, insights, next_steps.
    You are Aurora, an adaptive health coach.
    The reply must be easy to understand, direct, and detailed only where it helps.
    insights must contain exactly 2 short bullets.
    next_steps must contain exactly 3 practical actions.

    User profile: {profile or {}}
    Recent logs: {recent_logs[-5:]}
    Retrieved memories: {memory_hits[:5]}
    Derived analysis: {analysis}
    User message: {message}
    """
    response = generate_json(prompt, fallback)
    return {
        "reply": str(response.get("reply") or fallback["reply"]),
        "insights": [str(item) for item in (response.get("insights") or fallback["insights"])][:2],
        "next_steps": [str(item) for item in (response.get("next_steps") or fallback["next_steps"])][:3],
    }


def generate_chat_reply(message: str) -> str:
    lowered = message.lower()
    if "diet" in lowered or "meal" in lowered or "protein" in lowered:
        fallback = (
            "Start with a simple meal structure: build each meal around protein, add fruit or vegetables, "
            "use a steady carb source, and keep hydration consistent. If you want, ask for a full day of meals."
        )
    elif "workout" in lowered or "train" in lowered or "exercise" in lowered:
        fallback = (
            "Keep workouts simple: 3 strength sessions, 2 easier cardio or walking days, and at least 1 recovery day. "
            "If you share your goal and level, Aurora can make that much more specific."
        )
    elif "consisten" in lowered or "motivat" in lowered:
        fallback = (
            "Build consistency by shrinking the plan until it feels hard to skip. Start with a fixed workout window, "
            "a repeatable breakfast, and one end-of-day check-in."
        )
    else:
        fallback = (
            "I can help with workout planning, diet structure, recovery, cycle-aware guidance, and habit-building. "
            "Tell me your goal, current level, and biggest obstacle."
        )

    prompt = f"""
    You are Aurora, an in-app health and fitness guide.
    Reply in plain English.
    Keep the answer practical and easy to scan.
    If the question is broad, give a short answer plus 2 or 3 clear next options.

    User message: {message}
    """
    return generate_text(prompt=prompt, fallback=fallback)
