import numpy as np

from app.domain.entities.signal_features import SignalFeatures
from app.domain.entities.signal_window import SignalWindow
from app.domain.interfaces.signal_feature_extractor import ISignalFeatureExtractor


class FftFeatureExtractor(ISignalFeatureExtractor):
    def extract(self, window: SignalWindow) -> SignalFeatures:
        samples = np.asarray(window.samples, dtype=float)
        amplitude = float(samples.max() - samples.min())   # pico a pico

        centered = samples - samples.mean()                # quita el nivel DC
        spectrum = np.abs(np.fft.rfft(centered))
        freqs = np.fft.rfftfreq(len(samples), d=1.0 / window.sample_rate_hz)
        frequency = float(freqs[spectrum.argmax()]) if spectrum.any() else 0.0

        return SignalFeatures(amplitude=amplitude, frequency=frequency)