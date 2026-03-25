from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GeneratePlanRequest(BaseModel):
    name: Optional[str] = None
    goal: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    weight: float = Field(..., gt=0)
    gender: str = Field(..., min_length=1)
    height_cm: Optional[float] = Field(default=None, gt=0)
    cycle_phase: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=13, le=100)
    activity_level: Optional[str] = None
    pregnant: bool = False
    postpartum: bool = False
    pregnancy_trimester: Optional[int] = Field(default=None, ge=1, le=3)
    postpartum_weeks: Optional[int] = Field(default=None, ge=0, le=156)
    hormonal_concerns: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    lifestyle: Optional[Dict[str, Any]] = None


class GeneratePlanResponse(BaseModel):
    workout: str
    diet: str
    women_health: Optional[str] = None
