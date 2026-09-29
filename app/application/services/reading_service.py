from typing import Sequence

from app.application.services.session_service import SessionService
from app.domain.entities.session import Session
from app.domain.entities.signal_window import SignalWindow
from app.domain.interfaces.signal_feature_extractor import ISignalFeatureExtractor


class ReadingService:
    def __init__(self, session_service: SessionService,
                 extractor: ISignalFeatureExtractor):
        self._session_service = session_service
        self._extractor = extractor

    def finish_with_windows(self, session_id: int,
                            windows: Sequence[SignalWindow]) -> Session:
        features = [self._extractor.extract(w) for w in windows]
        return self._session_service.finish(session_id, features)