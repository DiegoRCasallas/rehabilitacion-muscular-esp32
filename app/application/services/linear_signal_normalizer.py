from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.signal_features import SignalFeatures
from app.domain.interfaces.signal_normalizer import ISignalNormalizer


class LinearSignalNormalizer(ISignalNormalizer):
    def normalize(self, features: SignalFeatures, profile: CalibrationProfile) -> float:
        span = profile.max_amplitude - profile.rest_amplitude
        level = (features.amplitude - profile.rest_amplitude) / span
        return max(0.0, min(1.0, level))