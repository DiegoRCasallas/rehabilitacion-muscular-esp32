from typing import Sequence

from app.domain.interfaces.score_calculator import IScoreCalculator


class ThresholdScoreCalculator(IScoreCalculator):
    def __init__(self, threshold: float = 0.5, points_per_sample: int = 1):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold debe estar entre 0 y 1")
        self._threshold = threshold
        self._points = points_per_sample

    def calculate(self, activations: Sequence[float]) -> int:
        return sum(self._points for a in activations if a >= self._threshold)