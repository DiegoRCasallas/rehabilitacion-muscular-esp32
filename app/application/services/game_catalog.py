from typing import List, Sequence

from app.domain.entities.activity import Activity
from app.domain.entities.game import GameDefinition, GameSpec
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.activity_repository import IActivityReader, IActivityWriter

GAME_SPECS = (
    GameSpec("dino", "Dino EMG",
             "Salta los obstáculos contrayendo el músculo. Entrena el ciclo contracción-relajación."),
    GameSpec("tracker", "Sigue la línea",
             "Mantén tu contracción dentro de la franja que sube y baja. Entrena el control gradual de la fuerza."),
)


class GameCatalogService:
    def __init__(self, reader: IActivityReader, writer: IActivityWriter,
                 specs: Sequence[GameSpec] = GAME_SPECS):
        self._reader = reader
        self._writer = writer
        self._specs = specs

    def ensure_seeded(self) -> None:
        existing = {a.name for a in self._reader.list_all()}
        for spec in self._specs:
            if spec.name not in existing:
                self._writer.add(Activity(name=spec.name))

    def list(self) -> List[GameDefinition]:
        ids = {a.name: a.id for a in self._reader.list_all()}
        return [GameDefinition(s.key, s.name, s.description, ids[s.name])
                for s in self._specs]

    def get(self, key: str) -> GameDefinition:
        for game in self.list():
            if game.key == key:
                return game
        raise NotFoundError(f"Juego {key} no existe")