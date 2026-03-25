from fastapi import APIRouter

from backend.models import GeneratePlanRequest, GeneratePlanResponse
from backend.services.ai_orchestrator import generate_full_plan


router = APIRouter()


@router.post("/generate-plan", response_model=GeneratePlanResponse)
def generate_plan(data: GeneratePlanRequest):
    return generate_full_plan(data.model_dump())
