from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.patient import Patient


class IPatientReader(ABC):
    @abstractmethod
    def get_by_id(self, patient_id: int) -> Optional[Patient]: ...

    @abstractmethod
    def list_all(self) -> List[Patient]: ...


class IPatientWriter(ABC):
    @abstractmethod
    def add(self, patient: Patient) -> Patient: ...