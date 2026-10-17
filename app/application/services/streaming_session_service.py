from app.application.services.live_session_service import LiveSessionService
from app.domain.entities.live_feedback import LiveFeedback
from app.domain.entities.signal_window import SignalWindow
from app.domain.interfaces.live_feedback_stream import ILiveFeedbackPublisher


class StreamingSessionService:
    def __init__(self, inner: LiveSessionService, publisher: ILiveFeedbackPublisher):
        self._inner = inner
        self._publisher = publisher

    def push_window(self, session_id: int, window: SignalWindow) -> LiveFeedback:
        feedback = self._inner.push_window(session_id, window)
        self._publisher.publish(feedback)
        return feedback