class BaseConfig:
    DATABASE_URL = "sqlite:///rehab.db"


class TestConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"