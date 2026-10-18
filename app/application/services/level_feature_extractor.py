from app.domain.entities.signal_features import SignalFeatures
from app.domain.entities.signal_window import SignalWindow
from app.domain.interfaces.signal_feature_extractor import ISignalFeatureExtractor


class LevelFeatureExtractor(ISignalFeatureExtractor):
    """Resume una ventana de envolvente EMG con su promedio (mV).
    La frecuencia no existe en una envolvente, así que se informa 0."""

    def extract(self, window: SignalWindow) -> SignalFeatures:
        level = sum(window.samples) / len(window.samples)
        return SignalFeatures(amplitude=max(0.0, level), frequency=0.0)