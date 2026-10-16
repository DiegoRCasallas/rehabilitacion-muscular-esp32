from zoneinfo import ZoneInfo

from app.application.services.catalog_services import (
    ActivityService, CalibrationService, PatientService)
from app.application.services.fft_feature_extractor import FftFeatureExtractor
from app.application.services.goal_policies import GoalPolicyFactory
from app.application.services.history_service import HistoryService
from app.application.services.linear_signal_normalizer import LinearSignalNormalizer
from app.application.services.live_session_service import LiveSessionService
from app.application.services.plan_service import PlanService
from app.application.services.query_services import (
    ActivityQueryService, CalibrationQueryService, PatientQueryService,
    PlanQueryService, SessionQueryService)
from app.application.services.reading_service import ReadingService
from app.application.services.recovery_service import RecoveryService
from app.application.services.score_progress_metric import ScoreProgressMetric
from app.application.services.session_service import SessionService
from app.application.services.threshold_score_calculator import ThresholdScoreCalculator
from app.infrastructure.database.base import create_session_factory
from app.infrastructure.live_state.in_memory_store import InMemoryLiveStateStore
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.plan_repository import SqlPlanRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository
from app.application.services.stale_session_service import StaleSessionService
from app.application.services.dashboard_service import DashboardService


class Container:
    def __init__(self, database_url: str, timezone_name: str = "UTC",
                 activation_threshold: float = 0.5):
        factory = create_session_factory(database_url)
        patients = SqlPatientRepository(factory)
        activities = SqlActivityRepository(factory)
        calibrations = SqlCalibrationRepository(factory)
        sessions = SqlSessionRepository(factory)
        plans = SqlPlanRepository(factory)
        tz = ZoneInfo(timezone_name)

        normalizer = LinearSignalNormalizer()
        score_calculator = ThresholdScoreCalculator(threshold=activation_threshold,
                                                    points_per_sample=10)
        extractor = FftFeatureExtractor()
        live_store = InMemoryLiveStateStore()

        self.patient_service = PatientService(patients, patients)
        self.activity_service = ActivityService(activities)
        self.calibration_service = CalibrationService(patients, calibrations)
        self.session_service = SessionService(
            patients, activities, calibrations, sessions, sessions,
            normalizer, score_calculator)
        self.reading_service = ReadingService(self.session_service, extractor)
        self.live_session_service = LiveSessionService(
            sessions, sessions, calibrations, extractor, normalizer,
            score_calculator, live_store, live_store)
        self.plan_service = PlanService(patients, plans, plans, sessions,
                                        GoalPolicyFactory(), tz=tz)
        self.recovery_service = RecoveryService(patients, sessions,
                                                ScoreProgressMetric(window=3))

        self.patient_query = PatientQueryService(patients)
        self.activity_query = ActivityQueryService(activities)
        self.calibration_query = CalibrationQueryService(patients, calibrations)
        self.plan_query = PlanQueryService(patients, plans)
        self.session_query = SessionQueryService(patients, sessions, tz=tz)
        self.history_service = HistoryService(patients, sessions, tz=tz)
        self.stale_session_service = StaleSessionService(sessions, sessions, live_store)
        self.dashboard_service = DashboardService(
            self.patient_service, self.calibration_query, self.plan_query,
            self.plan_service, self.history_service, self.recovery_service)