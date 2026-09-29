from dataclasses import dataclass


@dataclass(frozen=True)
class SignalFeatures:
    amplitude: float   # voltaje pico a pico (mV)
    frequency: float   # frecuencia dominante (Hz)

    def __post_init__(self):
        if self.amplitude < 0 or self.frequency < 0:
            raise ValueError("Amplitud y frecuencia no pueden ser negativas")