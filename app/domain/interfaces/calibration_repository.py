from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.calibration_profile import CalibrationProfile


class ICalibrationReader(ABC):
    @abstractmethod
    def get_by_id(self, calibration_id: int) -> Optional[CalibrationProfile]: ...

    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[CalibrationProfile]: ...


class ICalibrationWriter(ABC):
    @abstractmethod
    def save(self, profile: CalibrationProfile) -> CalibrationProfile: ...