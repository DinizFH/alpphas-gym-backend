import pytest
from app import create_app
from flask import json

class TestIntegridadeDados:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuários
        cls.client.post("/auth/register", json={
            "nome": "Nutricionista Teste",
            "email": "nutri@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "123456"
        })

        cls.client.post("/auth/register", json={
            "nome": "Personal Teste",
            "email": "personal@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF123"
        })

        cls.client.post("/auth/register", json={
            "nome": "Aluno Teste",
            "email": "aluno@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Logins
        cls.token_nutri = cls.client.post("/auth/login", json={
            "email": "nutri@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.token_personal = cls.client.post("/auth/login", json={
            "email": "personal@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.token_aluno = cls.client.post("/auth/login", json={
            "email": "aluno@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.headers_nutri = {"Authorization": f"Bearer {cls.token_nutri}"}
        cls.headers_personal = {"Authorization": f"Bearer {cls.token_personal}"}
        cls.headers_aluno = {"Authorization": f"Bearer {cls.token_aluno}"}

        # Buscar ID do aluno
        res_alunos = cls.client.get("/usuarios/alunos", headers=cls.headers_personal)
        cls.id_aluno = res_alunos.get_json()[0]["id_usuario"]

    def test_01_criar_avaliacao_sem_dobras(self):
        res = self.client.post("/avaliacoes/", headers=self.headers_personal, json={
            "id_aluno": self.id_aluno,
            "peso": 75,
            "altura": 1.75,
            "idade": 25,
            "observacoes": "Sem dobras cutâneas"
        })
        assert res.status_code == 400

    def test_02_criar_avaliacao_sem_peso_altura(self):
        res = self.client.post("/avaliacoes/", headers=self.headers_personal, json={
            "id_aluno": self.id_aluno,
            "idade": 25,
            "dobra_triceps": 12.5,
            "observacoes": "Sem peso/altura"
        })
        assert res.status_code == 400

    def test_03_criar_plano_sem_refeicoes(self):
        res = self.client.post("/planos/", headers=self.headers_nutri, json={
            "id_aluno": self.id_aluno,
            "refeicoes": []
        })
        assert res.status_code == 400

    def test_04_criar_plano_com_refeicao_sem_alimentos(self):
        res = self.client.post("/planos/", headers=self.headers_nutri, json={
            "id_aluno": self.id_aluno,
            "refeicoes": [
                {"titulo": "Café da Manhã", "calorias_estimadas": 300, "alimentos": []}
            ]
        })
        assert res.status_code in [200, 201]

    def test_05_criar_treino_sem_exercicios(self):
        res = self.client.post("/treinos/", headers=self.headers_personal, json={
            "id_aluno": self.id_aluno,
            "nome_treino": "Treino Vazio",
            "exercicios": []
        })
        assert res.status_code == 400

    def test_06_criar_registro_treino_sem_cargas(self):
        # Criar treino primeiro
        res_treino = self.client.post("/treinos/", headers=self.headers_personal, json={
            "id_aluno": self.id_aluno,
            "nome_treino": "Treino Registro",
            "exercicios": [{
                "id_exercicio": 1,
                "series": 3,
                "repeticoes": 10,
                "observacoes": "Simples"
            }]
        })
        id_treino = res_treino.get_json().get("id")

        # Criar registro com cargas vazias
        res_registro = self.client.post("/registrostreino/", headers=self.headers_aluno, json={
            "id_treino": id_treino,
            "observacoes": "Registro sem cargas",
            "cargas": []
        })
        assert res_registro.status_code == 400
