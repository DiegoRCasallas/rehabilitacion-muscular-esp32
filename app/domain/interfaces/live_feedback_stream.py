from abc import ABC, abstractmethod
from queue import Queue

from app.domain.entities.live_feedback import LiveFeedback


class ILiveFeedbackPublisher(ABC):
    @abstractmethod
    def publish(self, feedback: LiveFeedback) -> None: ...


class ILiveFeedbackSubscriber(ABC):
    @abstractmethod
    def subscribe(self, session_id: int) -> Queue: ...

    @abstractmethod
    def unsubscribe(self, session_id: int, queue: Queue) -> None: ...