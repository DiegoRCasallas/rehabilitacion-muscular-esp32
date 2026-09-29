from app.application.services.catalog_services import (
    ActivityService, CalibrationService, PatientService)
from app.application.services.fft_feature_extractor import FftFeatureExtractor
from app.application.services.linear_signal_normalizer import LinearSignalNormalizer
from app.application.services.reading_service import ReadingService
from app.application.services.session_service import SessionService
from app.application.services.threshold_score_calculator import ThresholdScoreCalculator
from app.infrastructure.database.base import create_session_factory
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository


class Container:
    def __init__(self, database_url: str):
        factory = create_session_factory(database_url)
        patients = SqlPatientRepository(factory)
        activities = SqlActivityRepository(factory)
        calibrations = SqlCalibrationRepository(factory)
        sessions = SqlSessionRepository(factory)

        self.patient_service = PatientService(patients, patients)
        self.activity_service = ActivityService(activities)
        self.calibration_service = CalibrationService(patients, calibrations)
        self.session_service = SessionService(
            patients, activities, calibrations, sessions, sessions,
            LinearSignalNormalizer(),
            ThresholdScoreCalculator(threshold=0.5, points_per_sample=10))
        self.reading_service = ReadingService(self.session_service,
                                              FftFeatureExtractor())