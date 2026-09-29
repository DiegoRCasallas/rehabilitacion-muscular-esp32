from dataclasses import dataclass


@dataclass(frozen=True)
class Progress:
    current: int
    target: int

    def __post_init__(self):
        if self.target <= 0:
            raise ValueError("target debe ser positivo")

    @property
    def completed(self) -> bool:
        return self.current >= self.target

    @property
    def percentage(self) -> float:
        return min(100.0, self.current / self.target * 100)


@dataclass(frozen=True)
class PlanProgress:
    goal: Progress    # avance hacia la meta del plan
    daily: Progress   # avance del objetivo diario