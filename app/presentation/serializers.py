from dataclasses import asdict
from datetime import date

from app.domain.entities.progress import PlanProgress, Progress


def serialize(entity) -> dict:
    # datetime es subclase de date, así que ambos se convierten a ISO
    return {k: (v.isoformat() if isinstance(v, date) else v)
            for k, v in asdict(entity).items()}


def _progress(p: Progress) -> dict:
    return {"current": p.current, "target": p.target,
            "percentage": p.percentage, "completed": p.completed}


def serialize_plan_progress(progress: PlanProgress) -> dict:
    return {"goal": _progress(progress.goal), "daily": _progress(progress.daily)}