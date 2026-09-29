from dataclasses import dataclass
from typing import Optional


@dataclass
class CalibrationProfile:
    patient_id: int
    label: str              # etiqueta descriptiva, sin lógica asociada
    rest_amplitude: float   # amplitud con el músculo relajado
    max_amplitude: float    # amplitud en contracción máxima voluntaria
    base_frequency: float   # frecuencia dominante de referencia
    id: Optional[int] = None

    def __post_init__(self):
        if not self.label.strip():
            raise ValueError("La calibración necesita una etiqueta")
        if self.max_amplitude <= self.rest_amplitude:
            raise ValueError("max_amplitude debe ser mayor que rest_amplitude")
        if self.base_frequency <= 0:
            raise ValueError("base_frequency debe ser positiva")