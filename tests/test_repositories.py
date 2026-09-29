from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository


def test_paciente_se_guarda_y_se_recupera(session_factory):
    repo = SqlPatientRepository(session_factory)
    saved = repo.add(Patient(full_name="Ana Pérez"))

    assert saved.id is not None
    assert repo.get_by_id(saved.id).full_name == "Ana Pérez"
    assert repo.get_by_id(999) is None


def test_calibraciones_se_listan_por_paciente(session_factory):
    patients = SqlPatientRepository(session_factory)
    calibrations = SqlCalibrationRepository(session_factory)
    ana = patients.add(Patient(full_name="Ana"))
    luis = patients.add(Patient(full_name="Luis"))

    calibrations.save(CalibrationProfile(patient_id=ana.id, label="Bíceps",
                                         rest_amplitude=0.1, max_amplitude=3.0,
                                         base_frequency=80))
    calibrations.save(CalibrationProfile(patient_id=luis.id, label="Antebrazo",
                                         rest_amplitude=0.2, max_amplitude=2.0,
                                         base_frequency=60))

    result = calibrations.list_by_patient(ana.id)
    assert [c.label for c in result] == ["Bíceps"]


def test_sesion_se_crea_y_se_actualiza_con_puntaje(session_factory):
    patient = SqlPatientRepository(session_factory).add(Patient(full_name="Ana"))
    activity = SqlActivityRepository(session_factory).add(Activity(name="Globos"))
    calibration = SqlCalibrationRepository(session_factory).save(
        CalibrationProfile(patient_id=patient.id, label="Bíceps",
                           rest_amplitude=0.1, max_amplitude=3.0, base_frequency=80))
    sessions = SqlSessionRepository(session_factory)

    created = sessions.add(Session(patient_id=patient.id, activity_id=activity.id,
                                   calibration_id=calibration.id))
    created.finish(150)
    sessions.update(created)

    stored = sessions.get_by_id(created.id)
    assert stored.score == 150
    assert stored.ended_at is not None
    assert stored.started_at.tzinfo is not None
    assert len(sessions.list_by_patient(patient.id)) == 1