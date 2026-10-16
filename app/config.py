class BaseConfig:
    DATABASE_URL = "sqlite:///rehab.db"
    TIMEZONE = "America/Bogota"
    ACTIVATION_THRESHOLD = 0.5


class TestConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"

