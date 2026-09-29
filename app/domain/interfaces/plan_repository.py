from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.rehabilitation_plan import RehabilitationPlan


class IPlanReader(ABC):
    @abstractmethod
    def get_by_id(self, plan_id: int) -> Optional[RehabilitationPlan]: ...

    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[RehabilitationPlan]: ...


class IPlanWriter(ABC):
    @abstractmethod
    def add(self, plan: RehabilitationPlan) -> RehabilitationPlan: ...