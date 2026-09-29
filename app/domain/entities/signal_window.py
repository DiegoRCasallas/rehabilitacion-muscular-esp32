from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SignalWindow:
    samples: Tuple[float, ...]   # voltaje en mV
    sample_rate_hz: float

    def __post_init__(self):
        if len(self.samples) < 2:
            raise ValueError("Una ventana necesita al menos 2 muestras")
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz debe ser positiva")