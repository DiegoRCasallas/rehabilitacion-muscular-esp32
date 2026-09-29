from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def create_session_factory(database_url: str) -> sessionmaker:
    options = {}
    if database_url.endswith(":memory:"):
        # Una sola conexión compartida, para que la BD en memoria no desaparezca
        options = dict(connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

    engine = create_engine(database_url, **options)

    from app.infrastructure.database import models  # noqa: F401 (registra las tablas)
    Base.metadata.create_all(engine)

    return sessionmaker(engine, expire_on_commit=False)