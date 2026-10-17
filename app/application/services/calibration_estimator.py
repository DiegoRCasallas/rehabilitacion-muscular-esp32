import statistics
from typing import Sequence

from app.domain.entities.calibration_run import CalibrationEstimate
from app.domain.entities.signal_features import SignalFeatures
from app.domain.interfaces.calibration_estimator import ICalibrationEstimator


class PercentileCalibrationEstimator(ICalibrationEstimator):
    def __init__(self, min_windows: int = 10, percentile: float = 0.9,
                 min_ratio: float = 2.0):
        self._min_windows = min_windows
        self._percentile = percentile
        self._min_ratio = min_ratio

    def estimate(self, rest: Sequence[SignalFeatures],
                 contraction: Sequence[SignalFeatures]) -> CalibrationEstimate:
        for name, items in (("reposo", rest), ("contracción", contraction)):
            if len(items) < self._min_windows:
                raise ValueError(
                    f"Muy pocas ventanas en {name} ({len(items)}); "
                    f"se necesitan al menos {self._min_windows}")

        rest_amplitude = statistics.median(f.amplitude for f in rest)
        amplitudes = sorted(f.amplitude for f in contraction)
        max_amplitude = amplitudes[int((len(amplitudes) - 1) * self._percentile)]

        if max_amplitude < rest_amplitude * self._min_ratio:
            raise ValueError("La contracción no supera con claridad el reposo: "
                             "revisa los electrodos y contrae con más fuerza")

        midpoint = rest_amplitude + 0.5 * (max_amplitude - rest_amplitude)
        frequency = statistics.median(
            f.frequency for f in contraction if f.amplitude >= midpoint)
        return CalibrationEstimate(rest_amplitude, max_amplitude, frequency)