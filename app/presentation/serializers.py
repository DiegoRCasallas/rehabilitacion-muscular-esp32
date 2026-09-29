from dataclasses import asdict
from datetime import datetime


def serialize(entity) -> dict:
    return {k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in asdict(entity).items()}