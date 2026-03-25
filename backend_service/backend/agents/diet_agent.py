from backend.core import generate_text


def generate_diet(data):
    prompt = f"""
    Create a diet plan.
    Goal: {data.get('goal')}
    Weight: {data.get('weight')}
    Level: {data.get('level')}
    Dietary restrictions: {', '.join(data.get('dietary_restrictions', []))}
    Hormonal concerns: {', '.join(data.get('hormonal_concerns', []))}
    Pregnant: {data.get('pregnant')}
    Postpartum: {data.get('postpartum')}
    Return a simple high-protein meal structure with hydration guidance.
    """

    if data.get("pregnant"):
        fallback = (
            "Pregnancy-aware diet plan: eat regular balanced meals with protein, complex carbs, fruit, vegetables, "
            "hydration, and clinician-guided prenatal nutrition support."
        )
    elif data.get("postpartum"):
        fallback = (
            "Postpartum diet plan: prioritize protein, hydration, iron-rich foods, fiber, and convenient nutrient-dense meals."
        )
    else:
        fallback = (
            f"Diet plan for {data.get('goal', 'fitness')}: prioritize lean protein, "
            "vegetables, whole grains, fruit, and 2.5 to 3 liters of water daily."
        )
    return generate_text(prompt=prompt, fallback=fallback)
