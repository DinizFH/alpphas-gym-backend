import pytest
from app import create_app
from flask import json


class TestPlanosAlimentares:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar nutricionista e aluno com nomes únicos
        cls.client.post("/auth/register", json={
            "nome": "Nutri Plano",
            "email": "nutri_plano@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN987"
        })
        cls.client.post("/auth/register", json={
            "nome": "Aluno Plano",
            "email": "aluno_plano@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login dos usuários
        res_nutri = cls.client.post("/auth/login", json={
            "email": "nutri_plano@teste.com",
            "senha": "123456"
        })
        cls.token_nutri = res_nutri.get_json()["access_token"]
        cls.headers_nutri = {"Authorization": f"Bearer {cls.token_nutri}"}

        res_aluno = cls.client.post("/auth/login", json={
            "email": "aluno_plano@teste.com",
            "senha": "123456"
        })
        cls.token_aluno = res_aluno.get_json()["access_token"]
        cls.headers_aluno = {"Authorization": f"Bearer {cls.token_aluno}"}

        # Buscar ID do aluno
        res = cls.client.get("/planos/buscar-aluno?nome=Aluno Plano", headers=cls.headers_nutri)
        assert res.status_code == 200
        cls.id_aluno = res.get_json()[0]["id_usuario"]

        # Criar plano alimentar inicial
        res = cls.client.post("/planos/", headers=cls.headers_nutri, json={
            "id_aluno": cls.id_aluno,
            "refeicoes": [
                {
                    "titulo": "Café da Manhã",
                    "calorias_estimadas": 300,
                    "alimentos": [
                        {"nome": "Ovo", "peso": 100},
                        {"nome": "Aveia", "peso": 50}
                    ]
                },
                {
                    "titulo": "Teste de erro",
                    "calorias_estimadas": 100,
                    "alimentos": [
                        {"nome": "", "peso": ""},  # Deve ser ignorado sem erro
                        {"nome": "Banana", "peso": 120}
                    ]
                }
            ]
        })
        assert res.status_code == 201

        # Obter ID do plano criado
        planos = cls.client.get("/planos/", headers=cls.headers_nutri).get_json()
        assert len(planos) > 0
        cls.id_plano = planos[0]["id_plano"]

    def test_01_listar_planos_nutricionista(self):
        res = self.client.get("/planos/", headers=self.headers_nutri)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_02_listar_planos_aluno(self):
        res = self.client.get("/planos/", headers=self.headers_aluno)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_03_detalhar_plano(self):
        res = self.client.get(f"/planos/{self.id_plano}", headers=self.headers_nutri)
        assert res.status_code == 200
        dados = res.get_json()
        assert "refeicoes" in dados
        assert dados["nome_aluno"].startswith("Aluno Plano")

    def test_04_editar_plano(self):
        novo_plano = {
            "refeicoes": [
                {
                    "titulo": "Almoço",
                    "calorias_estimadas": 600,
                    "alimentos": [
                        {"nome": "Arroz", "peso": 150},
                        {"nome": "Frango", "peso": 200},
                        {"nome": None, "peso": None}  # Deve ser ignorado sem erro
                    ]
                }
            ]
        }
        res = self.client.put(f"/planos/{self.id_plano}", headers=self.headers_nutri, json=novo_plano)
        assert res.status_code == 200
        assert res.get_json()["message"] == "Plano atualizado com sucesso"

    def test_05_excluir_plano(self):
        res = self.client.delete(f"/planos/{self.id_plano}", headers=self.headers_nutri)
        assert res.status_code == 200
        assert res.get_json()["message"] == "Plano desativado"
