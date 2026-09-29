from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Session:
    patient_id: int
    activity_id: int
    calibration_id: int
    started_at: datetime = field(default_factory=_now)
    ended_at: Optional[datetime] = None
    score: int = 0
    id: Optional[int] = None

    def finish(self, score: int) -> None:
        if score < 0:
            raise ValueError("El puntaje no puede ser negativo")
        self.score = score
        self.ended_at = _now()