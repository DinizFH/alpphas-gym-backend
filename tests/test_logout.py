import pytest
from app import create_app
from flask import json

class TestLogout:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuário de teste
        cls.client.post("/auth/register", json={
            "nome": "Usuário Logout",
            "email": "logout@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login
        res_login = cls.client.post("/auth/login", json={
            "email": "logout@teste.com",
            "senha": "123456"
        })
        cls.token = res_login.get_json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_01_logout_funciona(self):
        # Executa logout
        res = self.client.post("/auth/logout", headers=self.headers)
        assert res.status_code == 200
        assert "Logout realizado" in res.get_json().get("message", "")

    def test_02_token_revogado_bloqueia_acesso(self):
        # Após logout, tentar acessar rota protegida
        res = self.client.get("/usuarios/perfil", headers=self.headers)
        assert res.status_code == 401
        assert "revoked" in res.get_json().get("msg", "").lower()

