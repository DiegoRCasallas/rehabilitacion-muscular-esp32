from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyHistory:
    day: date
    sessions: int
    total_score: int