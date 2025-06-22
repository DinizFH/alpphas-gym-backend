# tests/test_dashboard.py

import pytest
from app import create_app
from app.extensions.db import get_db

class TestDashboard:

    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

        # Limpar o banco
        with cls.app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                for tabela in [
                    "registrostreino_exercicios", "registrostreino",
                    "treinoexercicios", "treinos", "exercicios",
                    "avaliacoesfisicas", "planosalimentares", "refeicoes",
                    "agendamentos", "usuarios", "tokensrevogados"
                ]:
                    cursor.execute(f"TRUNCATE TABLE {tabela}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                db.commit()

        # Criar usuários
        cls.client.post("/auth/register", json={
            "nome": "Aluno Dashboard",
            "email": "alunodash@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        cls.client.post("/auth/register", json={
            "nome": "Personal Dashboard",
            "email": "personaldash@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF1234"
        })
        cls.client.post("/auth/register", json={
            "nome": "Nutri Dashboard",
            "email": "nutridash@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN1234"
        })

        # Login
        cls.token_aluno = cls.client.post("/auth/login", json={
            "email": "alunodash@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.token_personal = cls.client.post("/auth/login", json={
            "email": "personaldash@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.token_nutri = cls.client.post("/auth/login", json={
            "email": "nutridash@teste.com", "senha": "123456"
        }).get_json()["access_token"]

    def test_01_dashboard_aluno(self):
        res = self.client.get("/dashboard/", headers={
            "Authorization": f"Bearer {self.token_aluno}"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["perfil"]["tipo_usuario"] == "aluno"
        assert "avaliacoes" in data
        assert "planos" in data
        assert "treinos" in data

    def test_02_dashboard_personal(self):
        res = self.client.get("/dashboard/", headers={
            "Authorization": f"Bearer {self.token_personal}"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["perfil"]["tipo_usuario"] == "personal"
        assert "proximos_atendimentos" in data
        assert "alunos_vinculados" in data

    def test_03_dashboard_nutricionista(self):
        res = self.client.get("/dashboard/", headers={
            "Authorization": f"Bearer {self.token_nutri}"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["perfil"]["tipo_usuario"] == "nutricionista"
        assert "proximos_atendimentos" in data
        assert "alunos_vinculados" in data
