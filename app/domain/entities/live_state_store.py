from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.live_feedback import LiveFeedback


class ILiveStateReader(ABC):
    @abstractmethod
    def get(self, session_id: int) -> Optional[LiveFeedback]: ...


class ILiveStateWriter(ABC):
    @abstractmethod
    def set(self, feedback: LiveFeedback) -> None: ...

    @abstractmethod
    def clear(self, session_id: int) -> None: ...