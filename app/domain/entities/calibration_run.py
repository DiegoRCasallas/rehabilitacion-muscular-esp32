from dataclasses import dataclass, field
from typing import List, Optional

from app.domain.entities.signal_features import SignalFeatures

PHASES = ("idle", "rest", "contraction")


@dataclass(frozen=True)
class CalibrationEstimate:
    rest_amplitude: float
    max_amplitude: float
    base_frequency: float


@dataclass(frozen=True)
class CalibrationRunStatus:
    run_id: int
    patient_id: int
    phase: str
    total_windows: int
    rest_windows: int
    contraction_windows: int
    last_amplitude: float


@dataclass
class CalibrationRun:
    patient_id: int
    id: Optional[int] = None
    phase: str = "idle"
    rest: List[SignalFeatures] = field(default_factory=list)
    contraction: List[SignalFeatures] = field(default_factory=list)
    total_windows: int = 0
    last_amplitude: float = 0.0

    def set_phase(self, phase: str) -> None:
        if phase not in PHASES:
            raise ValueError(f"Fase desconocida: {phase}")
        self.phase = phase

    def record(self, features: SignalFeatures) -> None:
        self.total_windows += 1
        self.last_amplitude = features.amplitude
        if self.phase == "rest":
            self.rest.append(features)
        elif self.phase == "contraction":
            self.contraction.append(features)

    def status(self) -> CalibrationRunStatus:
        return CalibrationRunStatus(
            run_id=self.id, patient_id=self.patient_id, phase=self.phase,
            total_windows=self.total_windows, rest_windows=len(self.rest),
            contraction_windows=len(self.contraction),
            last_amplitude=self.last_amplitude)