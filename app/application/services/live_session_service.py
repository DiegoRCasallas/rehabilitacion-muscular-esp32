from app.domain.entities.live_feedback import LiveFeedback
from app.domain.entities.session import Session
from app.domain.entities.signal_window import SignalWindow
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.calibration_repository import ICalibrationReader
from app.domain.interfaces.live_state_store import ILiveStateReader, ILiveStateWriter
from app.domain.interfaces.score_calculator import IScoreCalculator
from app.domain.interfaces.session_repository import ISessionReader, ISessionWriter
from app.domain.interfaces.signal_feature_extractor import ISignalFeatureExtractor
from app.domain.interfaces.signal_normalizer import ISignalNormalizer


class LiveSessionService:
    def __init__(
        self,
        session_reader: ISessionReader,
        session_writer: ISessionWriter,
        calibrations: ICalibrationReader,
        extractor: ISignalFeatureExtractor,
        normalizer: ISignalNormalizer,
        score_calculator: IScoreCalculator,
        state_reader: ILiveStateReader,
        state_writer: ILiveStateWriter,
    ):
        self._session_reader = session_reader
        self._session_writer = session_writer
        self._calibrations = calibrations
        self._extractor = extractor
        self._normalizer = normalizer
        self._score_calculator = score_calculator
        self._state_reader = state_reader
        self._state_writer = state_writer

    def push_window(self, session_id: int, window: SignalWindow) -> LiveFeedback:
        session = self._load_open(session_id)
        profile = self._calibrations.get_by_id(session.calibration_id)

        features = self._extractor.extract(window)
        activation = self._normalizer.normalize(features, profile)

        session.add_points(self._score_calculator.calculate([activation]))
        self._session_writer.update(session)

        previous = self._state_reader.get(session_id)
        feedback = LiveFeedback(
            session_id=session_id, activation=activation,
            amplitude=features.amplitude, frequency=features.frequency,
            score=session.score,
            windows_received=(previous.windows_received if previous else 0) + 1)
        self._state_writer.set(feedback)
        return feedback

    def get_live(self, session_id: int) -> LiveFeedback:
        feedback = self._state_reader.get(session_id)
        if feedback is None:
            raise NotFoundError(f"Sesión {session_id} sin lecturas en vivo")
        return feedback

    def close(self, session_id: int) -> Session:
        session = self._load_open(session_id)
        session.finish(session.score)      # conserva el puntaje acumulado
        saved = self._session_writer.update(session)
        self._state_writer.clear(session_id)
        return saved

    def _load_open(self, session_id: int) -> Session:
        session = self._session_reader.get_by_id(session_id)
        if session is None:
            raise NotFoundError(f"Sesión {session_id} no existe")
        if session.ended_at is not None:
            raise ValueError("La sesión ya fue finalizada")
        return session