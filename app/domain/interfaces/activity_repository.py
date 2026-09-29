from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.activity import Activity


class IActivityReader(ABC):
    @abstractmethod
    def get_by_id(self, activity_id: int) -> Optional[Activity]: ...

    @abstractmethod
    def list_all(self) -> List[Activity]: ...


class IActivityWriter(ABC):
    @abstractmethod
    def add(self, activity: Activity) -> Activity: ...