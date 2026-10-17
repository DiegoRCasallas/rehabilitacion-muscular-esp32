from queue import Empty, Full, Queue
from threading import Lock
from typing import Dict, List

from app.domain.entities.live_feedback import LiveFeedback
from app.domain.interfaces.live_feedback_stream import (
    ILiveFeedbackPublisher, ILiveFeedbackSubscriber)


class LiveFeedbackHub(ILiveFeedbackPublisher, ILiveFeedbackSubscriber):
    """Reparte el feedback en memoria. Cada suscriptor conserva solo el más reciente."""

    def __init__(self):
        self._subscribers: Dict[int, List[Queue]] = {}
        self._lock = Lock()

    def subscribe(self, session_id: int) -> Queue:
        queue: Queue = Queue(maxsize=1)
        with self._lock:
            self._subscribers.setdefault(session_id, []).append(queue)
        return queue

    def unsubscribe(self, session_id: int, queue: Queue) -> None:
        with self._lock:
            queues = self._subscribers.get(session_id, [])
            if queue in queues:
                queues.remove(queue)
            if not queues:
                self._subscribers.pop(session_id, None)

    def publish(self, feedback: LiveFeedback) -> None:
        with self._lock:
            for queue in self._subscribers.get(feedback.session_id, []):
                try:
                    queue.put_nowait(feedback)
                except Full:
                    try:
                        queue.get_nowait()       # descarta el dato viejo
                    except Empty:
                        pass
                    queue.put_nowait(feedback)