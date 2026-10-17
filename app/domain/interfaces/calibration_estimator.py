from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.entities.calibration_run import CalibrationEstimate
from app.domain.entities.signal_features import SignalFeatures


class ICalibrationEstimator(ABC):
    @abstractmethod
    def estimate(self, rest: Sequence[SignalFeatures],
                 contraction: Sequence[SignalFeatures]) -> CalibrationEstimate: ...