def build_profile_summary(profile: dict) -> str:
    lifestyle = profile.get("lifestyle", {})
    concerns = profile.get("hormonal_concerns") or ["no major hormonal concerns logged"]
    diet_flags = profile.get("dietary_restrictions") or ["no dietary restrictions"]

    return (
        f"{profile.get('name')} is focused on {profile.get('goal')} at a {profile.get('level')} level. "
        f"Lifestyle shows {lifestyle.get('sleep_hours', 'unknown')} hours of sleep, "
        f"{lifestyle.get('water_liters', 'unknown')}L water, and stress level "
        f"{lifestyle.get('stress_level', 'unknown')}/10. Hormonal concerns: {', '.join(concerns)}. "
        f"Dietary restrictions: {', '.join(diet_flags)}."
    )
