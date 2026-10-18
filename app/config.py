class BaseConfig:
    DATABASE_URL = "sqlite:///rehab.db"
    TIMEZONE = "America/Bogota"
    ACTIVATION_THRESHOLD = 0.5
    SIGNAL_MODE = "level"      # "level" = envolvente (promedio), "wave" = onda con FFT


class TestConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    SIGNAL_MODE = "wave"       # los tests existentes usan senoides