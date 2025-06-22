import pytest
from app import create_app
from app.extensions.db import get_db
from werkzeug.security import generate_password_hash

class TestLoginAdmin:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        cls.admin_email = "administrador@alpphasgym.com"
        cls.admin_senha = "123456"
        senha_hash = generate_password_hash(cls.admin_senha)

        with cls.app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, ativo)
                    VALUES (%s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE senha_hash = VALUES(senha_hash)
                """, ("Administrador", cls.admin_email, senha_hash, "admin"))
            db.commit()

    def test_01_login_admin(self):
        res = self.client.post("/auth/login", json={
            "email": self.admin_email,
            "senha": self.admin_senha
        })
        assert res.status_code == 200
        json_data = res.get_json()
        assert "access_token" in json_data
        self.__class__.token_admin = json_data["access_token"]

    def test_02_acesso_estatisticas_com_token_admin(self):
        res = self.client.get(
            "/admin/estatisticas",
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        assert res.status_code == 200
        dados = res.get_json()
        assert "alunos" in dados
        assert "planos" in dados

    def test_03_usuario_comum_nao_acessa_estatisticas(self):
        # Criar e logar um aluno comum
        self.client.post("/auth/register", json={
            "nome": "Aluno Teste",
            "email": "aluno@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        res_login = self.client.post("/auth/login", json={
            "email": "aluno@teste.com",
            "senha": "123456"
        })
        token_aluno = res_login.get_json()["access_token"]

        res = self.client.get(
            "/admin/estatisticas",
            headers={"Authorization": f"Bearer {token_aluno}"}
        )
        assert res.status_code == 403
