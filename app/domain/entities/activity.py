from dataclasses import dataclass
from typing import Optional


@dataclass
class Activity:
    name: str
    id: Optional[int] = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("El nombre de la actividad es obligatorio")