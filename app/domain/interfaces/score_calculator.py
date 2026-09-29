from abc import ABC, abstractmethod
from typing import Sequence


class IScoreCalculator(ABC):
    @abstractmethod
    def calculate(self, activations: Sequence[float]) -> int:
        """Recibe activaciones normalizadas (0.0 a 1.0) y devuelve el puntaje."""