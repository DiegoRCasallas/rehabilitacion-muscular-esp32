from typing import Callable, Dict, Sequence

from app.domain.entities.progress import Progress
from app.domain.entities.session import Session
from app.domain.interfaces.goal_policy import IGoalPolicy


class SessionCountGoal(IGoalPolicy):
    def __init__(self, target: int):
        self._target = target

    def evaluate(self, sessions: Sequence[Session]) -> Progress:
        return Progress(current=len(sessions), target=self._target)


class TotalScoreGoal(IGoalPolicy):
    def __init__(self, target: int):
        self._target = target

    def evaluate(self, sessions: Sequence[Session]) -> Progress:
        return Progress(current=sum(s.score for s in sessions), target=self._target)


class GoalPolicyFactory:
    def __init__(self):
        self._builders: Dict[str, Callable[[int], IGoalPolicy]] = {
            "sessions": SessionCountGoal,
            "score": TotalScoreGoal,
        }

    def register(self, goal_type: str, builder: Callable[[int], IGoalPolicy]) -> None:
        self._builders[goal_type] = builder

    def create(self, goal_type: str, target: int) -> IGoalPolicy:
        builder = self._builders.get(goal_type)
        if builder is None:
            raise ValueError(f"Tipo de meta desconocido: {goal_type}")
        return builder(target)