from datetime import datetime
from datetime import date  
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class PatientModel(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200))


class ActivityModel(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class CalibrationModel(Base):
    __tablename__ = "calibrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    rest_amplitude: Mapped[float] = mapped_column(Float)
    max_amplitude: Mapped[float] = mapped_column(Float)
    base_frequency: Mapped[float] = mapped_column(Float)


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    calibration_id: Mapped[int] = mapped_column(ForeignKey("calibrations.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)

class PlanModel(Base):
    __tablename__ = "rehabilitation_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    goal_type: Mapped[str] = mapped_column(String(30))
    goal_target: Mapped[int] = mapped_column(Integer)
    daily_score_goal: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)