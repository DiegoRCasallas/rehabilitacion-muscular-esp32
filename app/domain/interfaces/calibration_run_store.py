from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.calibration_run import CalibrationRun


class ICalibrationRunReader(ABC):
    @abstractmethod
    def get(self, run_id: int) -> Optional[CalibrationRun]: ...

    @abstractmethod
    def get_active_for_patient(self, patient_id: int) -> Optional[CalibrationRun]: ...


class ICalibrationRunWriter(ABC):
    @abstractmethod
    def add(self, run: CalibrationRun) -> CalibrationRun: ...

    @abstractmethod
    def remove(self, run_id: int) -> None: ...