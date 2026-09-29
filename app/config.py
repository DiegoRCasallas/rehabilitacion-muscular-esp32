class BaseConfig:
    DATABASE_URL = "sqlite:///rehab.db"
    TIMEZONE = "America/Bogota"


class TestConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"