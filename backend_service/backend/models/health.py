from typing import List, Optional

from pydantic import BaseModel, Field


class LifestyleProfile(BaseModel):
    sleep_hours: float = Field(..., ge=0, le=24)
    water_liters: float = Field(..., ge=0, le=10)
    stress_level: int = Field(..., ge=1, le=10)
    activity_level: str = Field(..., min_length=2)
    dietary_preference: str = Field(..., min_length=2)
    health_goals: List[str] = Field(default_factory=list)


class UserProfileRequest(BaseModel):
    user_id: Optional[str] = None
    name: str = Field(..., min_length=2)
    age: int = Field(..., ge=13, le=100)
    gender: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    goal: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    pregnant: bool = False
    postpartum: bool = False
    pregnancy_trimester: Optional[int] = Field(default=None, ge=1, le=3)
    postpartum_weeks: Optional[int] = Field(default=None, ge=0, le=156)
    hormonal_concerns: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    lifestyle: LifestyleProfile


class UserProfileResponse(BaseModel):
    user_id: str
    saved: bool
    summary: str
    profile: dict


class PeriodLogRequest(BaseModel):
    user_id: Optional[str] = None
    start_date: str = Field(..., min_length=8)
    end_date: str = Field(..., min_length=8)
    symptoms: List[str] = Field(default_factory=list)
    flow_level: str = Field(default="moderate")
    mood: str = Field(default="stable")
    cravings: List[str] = Field(default_factory=list)
    notes: str = Field(default="")


class SymptomInsight(BaseModel):
    flag: str
    detail: str


class CyclePredictionResponse(BaseModel):
    user_id: str
    average_cycle_length: Optional[int] = None
    average_period_length: Optional[int] = None
    next_period_start: Optional[str] = None
    predicted_phase: str
    irregularity_score: str
    recent_logs: List[dict] = Field(default_factory=list)
    possible_concerns: List[SymptomInsight] = Field(default_factory=list)
    nutrition_focus: List[str] = Field(default_factory=list)
    workout_focus: List[str] = Field(default_factory=list)
    disclaimer: str


class StreakCheckInRequest(BaseModel):
    user_id: Optional[str] = None
    date: Optional[str] = None
    workout_completed: bool = True
    nutrition_completed: bool = False
    journal_note: str = Field(default="")


class StreakResponse(BaseModel):
    user_id: str
    current_streak: int
    longest_streak: int
    total_checkins: int
    motivation: str
    last_checkin: Optional[str] = None


class ProgressLogRequest(BaseModel):
    user_id: Optional[str] = None
    date: Optional[str] = None
    weight: Optional[float] = Field(default=None, gt=0)
    energy_level: int = Field(..., ge=1, le=10)
    mood: str = Field(..., min_length=2)
    workout_minutes: int = Field(..., ge=0, le=500)
    adherence_score: int = Field(..., ge=1, le=10)
    notes: str = Field(default="")


class ProgressCoachRequest(BaseModel):
    user_id: Optional[str] = None
    message: str = Field(..., min_length=2)


class ProgressCoachResponse(BaseModel):
    reply: str
    insights: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class WorkoutLogRequest(BaseModel):
    date: Optional[str] = None
    workout_type: str = Field(..., min_length=2)
    duration_minutes: int = Field(..., ge=0, le=500)
    intensity: str = Field(..., min_length=2)
    completed: bool = True
    notes: str = Field(default="")


class DietLogRequest(BaseModel):
    date: Optional[str] = None
    meals_followed: int = Field(..., ge=0, le=10)
    hydration_liters: float = Field(..., ge=0, le=10)
    protein_grams: Optional[int] = Field(default=None, ge=0, le=500)
    cravings: List[str] = Field(default_factory=list)
    notes: str = Field(default="")


class FeedbackRequest(BaseModel):
    category: str = Field(..., min_length=2)
    feedback: str = Field(..., min_length=3)
    rating: Optional[int] = Field(default=None, ge=1, le=10)


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)


class HistoryResponse(BaseModel):
    workout_logs: List[dict] = Field(default_factory=list)
    diet_logs: List[dict] = Field(default_factory=list)
    progress_logs: List[dict] = Field(default_factory=list)
    period_logs: List[dict] = Field(default_factory=list)
    recent_memories: List[dict] = Field(default_factory=list)


class WeeklyReportResponse(BaseModel):
    user_id: str
    period_start: str
    period_end: str
    summary: str
    wins: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
