from fastapi import APIRouter, Depends

from backend.core.auth import get_current_user
from backend.models.health import (
    DietLogRequest,
    FeedbackRequest,
    HistoryResponse,
    MemorySearchRequest,
    WeeklyReportResponse,
    WorkoutLogRequest,
)
from backend.services.tracking_service import (
    generate_weekly_report,
    get_history,
    log_diet,
    log_workout,
    save_feedback,
)
from backend.services.memory_service import search_memories


router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/workout")
def create_workout_log(data: WorkoutLogRequest, current_user: dict = Depends(get_current_user)):
    return log_workout(current_user["user_id"], data.model_dump())


@router.post("/diet")
def create_diet_log(data: DietLogRequest, current_user: dict = Depends(get_current_user)):
    return log_diet(current_user["user_id"], data.model_dump())


@router.post("/feedback")
def create_feedback(data: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    return save_feedback(current_user["user_id"], data.category, data.feedback, data.rating)


@router.get("/history", response_model=HistoryResponse)
def history(current_user: dict = Depends(get_current_user)):
    return get_history(current_user["user_id"])


@router.post("/memory-search")
def memory_search(data: MemorySearchRequest, current_user: dict = Depends(get_current_user)):
    return {
        "query": data.query,
        "results": search_memories(current_user["user_id"], data.query, top_k=data.top_k),
    }


@router.get("/weekly-report", response_model=WeeklyReportResponse)
def weekly_report(current_user: dict = Depends(get_current_user)):
    return generate_weekly_report(current_user["user_id"])
