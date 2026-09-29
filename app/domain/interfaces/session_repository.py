from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.session import Session


class ISessionReader(ABC):
    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[Session]: ...

    @abstractmethod
    def list_by_patient(self, patient_id: int) -> List[Session]: ...


class ISessionWriter(ABC):
    @abstractmethod
    def add(self, session: Session) -> Session: ...

    @abstractmethod
    def update(self, session: Session) -> Session: ...