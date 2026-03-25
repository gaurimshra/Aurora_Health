from backend.services.agentic_ai_service import generate_plan_response


def generate_full_plan(user_data):
    return generate_plan_response(user_data)
