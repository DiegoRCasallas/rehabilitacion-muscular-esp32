from dataclasses import dataclass


@dataclass(frozen=True)
class LiveFeedback:
    session_id: int
    activation: float        # 0.0 a 1.0, ya calibrada
    amplitude: float
    frequency: float         # reservada para un futuro índice de fatiga
    score: int               # puntaje acumulado hasta ahora
    windows_received: int