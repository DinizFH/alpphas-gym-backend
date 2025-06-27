import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "Joao#123!")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "wT8p@Alpph@s$eGur4")

    DB_CONFIG = {
        'host': os.getenv("DB_HOST", "alpphasgym-db.cd6g2sg0apgt.us-east-2.rds.amazonaws.com"),
        'user': os.getenv("DB_USER", "root"),
        'password': os.getenv("DB_PASSWORD", "jvbPjdbLCb3UoyKeHnNH5joqnEjD8MBbAcF2"),
        'database': os.getenv("DB_NAME", "alpphas_gym"),
        'port': int(os.getenv("DB_PORT", 3306))
    }

    # Outras configurações úteis (opcional)
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    TESTING = os.getenv("FLASK_ENV") == "testing"
