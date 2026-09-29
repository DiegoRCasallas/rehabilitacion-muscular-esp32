from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class RehabilitationPlan:
    patient_id: int
    name: str
    goal_type: str          # "sessions" o "score" (lo resuelve la fábrica)
    goal_target: int
    daily_score_goal: int
    start_date: date
    active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("El plan necesita un nombre")
        if self.goal_target <= 0:
            raise ValueError("goal_target debe ser positivo")
        if self.daily_score_goal <= 0:
            raise ValueError("daily_score_goal debe ser positivo")