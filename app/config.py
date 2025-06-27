import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    DB_CONFIG = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_NAME"),
        'port': int(os.getenv("DB_PORT", 3306))
    }

    # Acesso rápido às variáveis separadas
    DB_HOST = DB_CONFIG["host"]
    DB_USER = DB_CONFIG["user"]
    DB_PASSWORD = DB_CONFIG["password"]
    DB_NAME = DB_CONFIG["database"]
    DB_PORT = DB_CONFIG["port"]

    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    TESTING = os.getenv("FLASK_ENV") == "testing"
