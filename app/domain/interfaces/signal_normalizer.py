from abc import ABC, abstractmethod

from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.signal_features import SignalFeatures


class ISignalNormalizer(ABC):
    @abstractmethod
    def normalize(self, features: SignalFeatures, profile: CalibrationProfile) -> float:
        """Devuelve el nivel de activación muscular entre 0.0 y 1.0."""