from threading import Lock
from typing import Dict, Optional

from app.domain.entities.calibration_run import CalibrationRun
from app.domain.interfaces.calibration_run_store import (
    ICalibrationRunReader, ICalibrationRunWriter)


class InMemoryCalibrationRunStore(ICalibrationRunReader, ICalibrationRunWriter):
    def __init__(self):
        self._runs: Dict[int, CalibrationRun] = {}
        self._next_id = 1
        self._lock = Lock()

    def add(self, run: CalibrationRun) -> CalibrationRun:
        with self._lock:
            run.id = self._next_id
            self._next_id += 1
            self._runs[run.id] = run
            return run

    def get(self, run_id: int) -> Optional[CalibrationRun]:
        with self._lock:
            return self._runs.get(run_id)

    def get_active_for_patient(self, patient_id: int) -> Optional[CalibrationRun]:
        with self._lock:
            mine = [r for r in self._runs.values() if r.patient_id == patient_id]
            return mine[-1] if mine else None     # el dict conserva el orden de inserción

    def remove(self, run_id: int) -> None:
        with self._lock:
            self._runs.pop(run_id, None)