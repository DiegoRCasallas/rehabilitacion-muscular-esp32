from app import create_app
from app.config import TestConfig


def test_health():
    client = create_app(TestConfig).test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}