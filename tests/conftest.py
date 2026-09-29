import pytest

from app.infrastructure.database.base import create_session_factory


@pytest.fixture
def session_factory():
    return create_session_factory("sqlite:///:memory:")