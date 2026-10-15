from threading import Lock
from typing import Dict, Optional

from app.domain.entities.live_feedback import LiveFeedback
from app.domain.interfaces.live_state_store import ILiveStateReader, ILiveStateWriter


class InMemoryLiveStateStore(ILiveStateReader, ILiveStateWriter):
    def __init__(self):
        self._data: Dict[int, LiveFeedback] = {}
        self._lock = Lock()

    def get(self, session_id: int) -> Optional[LiveFeedback]:
        with self._lock:
            return self._data.get(session_id)

    def set(self, feedback: LiveFeedback) -> None:
        with self._lock:
            self._data[feedback.session_id] = feedback

    def clear(self, session_id: int) -> None:
        with self._lock:
            self._data.pop(session_id, None)