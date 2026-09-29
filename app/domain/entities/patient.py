from dataclasses import dataclass
from typing import Optional


@dataclass
class Patient:
    full_name: str
    id: Optional[int] = None

    def __post_init__(self):
        if not self.full_name.strip():
            raise ValueError("El nombre del paciente es obligatorio")