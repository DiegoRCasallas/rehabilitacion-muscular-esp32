from datetime import timezone, tzinfo
from typing import Dict, List, Tuple

from app.domain.entities.daily_history import DailyHistory
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.session_repository import ISessionReader


class HistoryService:
    def __init__(self, patients: IPatientReader, sessions: ISessionReader,
                 tz: tzinfo = timezone.utc):
        self._patients = patients
        self._sessions = sessions
        self._tz = tz

    def daily(self, patient_id: int) -> List[DailyHistory]:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")

        totals: Dict = {}
        for s in self._sessions.list_by_patient(patient_id):
            if s.ended_at is None:      # las sesiones abiertas no cuentan
                continue
            day = s.started_at.astimezone(self._tz).date()
            count, score = totals.get(day, (0, 0))
            totals[day] = (count + 1, score + s.score)

        return [DailyHistory(day=d, sessions=c, total_score=sc)
                for d, (c, sc) in sorted(totals.items())]
    