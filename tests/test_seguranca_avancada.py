import pytest
from app import create_app
from flask_jwt_extended import create_access_token
from datetime import timedelta
import json

class TestSegurancaAvancada:

    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Registrar um usuário
        cls.client.post("/auth/register", json={
            "nome": "Usuário Seguranca",
            "email": "seguranca@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        res = cls.client.post("/auth/login", json={
            "email": "seguranca@teste.com",
            "senha": "123456"
        })
        cls.token_valido = res.get_json()["access_token"]

        # Criar token inválido (aleatório)
        cls.token_invalido = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.INVALID_TOKEN"

        # Criar token expirado (simulado com timedelta negativo)
        with cls.app.app_context():
            cls.token_expirado = create_access_token(
                identity=json.dumps({"id": 999, "tipo_usuario": "aluno"}),
                expires_delta=timedelta(seconds=-10)
            )

    def test_01_token_ausente(self):
        res = self.client.get("/usuarios/perfil")
        assert res.status_code == 401

    def test_02_token_invalido(self):
        res = self.client.get("/usuarios/perfil", headers={
            "Authorization": self.token_invalido
        })
        assert res.status_code == 422 or res.status_code == 401

    def test_03_token_expirado(self):
        res = self.client.get("/usuarios/perfil", headers={
            "Authorization": f"Bearer {self.token_expirado}"
        })
        assert res.status_code == 401

    def test_04_token_valido_funciona(self):
        res = self.client.get("/usuarios/perfil", headers={
            "Authorization": f"Bearer {self.token_valido}"
        })
        assert res.status_code == 200
