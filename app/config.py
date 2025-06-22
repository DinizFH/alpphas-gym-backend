import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "Joao#123!")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "wT8p@Alpph@s$eGur4")

    DB_CONFIG = {
        'host': os.getenv("DB_HOST", "127.0.0.1"),
        'user': os.getenv("DB_USER", "root"),
        'password': os.getenv("DB_PASSWORD", "Diniz@3582"),
        'database': os.getenv("DB_NAME", "alpphas_gym_test"),
        'port': int(os.getenv("DB_PORT", 3307))
    }

    # Outras configurações úteis (opcional)
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    TESTING = os.getenv("FLASK_ENV") == "testing"
