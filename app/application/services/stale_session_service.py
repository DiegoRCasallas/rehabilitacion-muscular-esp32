from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.domain.entities.session import Session
from app.domain.interfaces.live_state_store import ILiveStateWriter
from app.domain.interfaces.session_repository import IOpenSessionReader, ISessionWriter


class StaleSessionService:
    def __init__(self, open_reader: IOpenSessionReader, writer: ISessionWriter,
                 state_writer: ILiveStateWriter):
        self._open_reader = open_reader
        self._writer = writer
        self._state_writer = state_writer

    def close_stale(self, max_age_minutes: int,
                    now: Optional[datetime] = None) -> List[Session]:
        if max_age_minutes < 1:
            raise ValueError("max_age_minutes debe ser al menos 1")
        now = now or datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=max_age_minutes)

        closed = []
        for session in self._open_reader.list_open():
            if session.started_at < cutoff:
                session.finish(session.score)       # conserva lo acumulado
                closed.append(self._writer.update(session))
                self._state_writer.clear(session.id)
        return closed