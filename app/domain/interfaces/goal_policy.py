from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.progress import Progress
from app.domain.entities.session import Session


class IGoalPolicy(ABC):
    @abstractmethod
    def evaluate(self, sessions: Sequence[Session]) -> Progress:
        """Mide el avance hacia la meta a partir de las sesiones finalizadas."""