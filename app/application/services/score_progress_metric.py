from typing import Sequence

from app.domain.entities.session import Session
from app.domain.interfaces.recovery_metric import IRecoveryMetric


class ScoreProgressMetric(IRecoveryMetric):
    def __init__(self, window: int = 3):
        if window < 1:
            raise ValueError("window debe ser al menos 1")
        self._window = window

    def calculate(self, sessions: Sequence[Session]) -> float:
        finished = sorted((s for s in sessions if s.ended_at is not None),
                          key=lambda s: s.started_at)
        if len(finished) < 2 * self._window:
            return 0.0  # historial insuficiente para comparar

        first = self._average(finished[:self._window])
        last = self._average(finished[-self._window:])
        if first == 0:
            return 0.0
        return (last - first) / first * 100

    @staticmethod
    def _average(sessions: Sequence[Session]) -> float:
        return sum(s.score for s in sessions) / len(sessions)