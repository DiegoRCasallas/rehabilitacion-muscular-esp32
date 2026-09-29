class BaseConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///rehab.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"