import pytest
import os
from dotenv import load_dotenv

# Carrega .env de teste
load_dotenv(dotenv_path=".env.test")

from app import create_app
from app.extensions.db import get_db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True

    assert app.config["DB_NAME"] == "alpphas_gym_test", (
        "⚠️ Você está tentando rodar os testes em um banco que não é de testes!"
    )

    return app

@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def limpar_banco(app):
    with app.app_context():
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                tabelas = [
                    "registrostreino_exercicios",
                    "registrostreino",
                    "treinoexercicios",
                    "treinos",
                    "exercicios",
                    "avaliacoesfisicas",
                    "planosalimentares",
                    "refeicoes",
                    "agendamentos",
                    "usuarios",
                    "tokensrevogados"
                ]
                for tabela in tabelas:
                    cursor.execute(f"TRUNCATE TABLE {tabela}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                db.commit()
        except Exception as e:
            print("[ERRO LIMPEZA DB]", e)
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            db.rollback()
        finally:
            db.close()
