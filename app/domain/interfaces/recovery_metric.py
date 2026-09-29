from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.session import Session


class IRecoveryMetric(ABC):
    @abstractmethod
    def calculate(self, sessions: Sequence[Session]) -> float:
        """Devuelve un porcentaje de recuperación a partir del historial."""