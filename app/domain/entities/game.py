from dataclasses import dataclass


@dataclass(frozen=True)
class GameSpec:
    key: str
    name: str
    description: str


@dataclass(frozen=True)
class GameDefinition:
    key: str
    name: str
    description: str
    activity_id: int