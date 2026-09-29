from abc import ABC, abstractmethod

from app.domain.entities.signal_features import SignalFeatures
from app.domain.entities.signal_window import SignalWindow


class ISignalFeatureExtractor(ABC):
    @abstractmethod
    def extract(self, window: SignalWindow) -> SignalFeatures: ...