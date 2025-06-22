import pytest
from app import create_app
from app.extensions.db import get_db

@pytest.fixture(scope="function")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="function")
def client(app):
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

    with app.test_client() as client:
        yield client
