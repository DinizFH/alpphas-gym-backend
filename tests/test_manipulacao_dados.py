import pytest
from app import create_app
from app.extensions.db import get_db

class TestManipulacaoDados:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuários
        cls.client.post("/auth/register", json={
            "nome": "Nutri Dados",
            "email": "nutrid@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN001"
        })
        cls.client.post("/auth/register", json={
            "nome": "Personal Dados",
            "email": "personald@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF001"
        })
        cls.client.post("/auth/register", json={
            "nome": "Aluno Dados",
            "email": "alunod@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Logins
        cls.token_nutri = cls.client.post("/auth/login", json={
            "email": "nutrid@teste.com", "senha": "123456"
        }).get_json()["access_token"]
        cls.token_personal = cls.client.post("/auth/login", json={
            "email": "personald@teste.com", "senha": "123456"
        }).get_json()["access_token"]
        cls.token_aluno = cls.client.post("/auth/login", json={
            "email": "alunod@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        # Criar plano como nutricionista com ID inválido
        res = cls.client.post("/planos/", json={
            "id_aluno": 9999,  # ID inválido proposital
            "refeicoes": [{
                "titulo": "Almoço",
                "calorias_estimadas": 500,
                "alimentos": [{"nome": "Arroz", "peso": 100}]
            }]
        }, headers={"Authorization": f"Bearer {cls.token_nutri}"})
        cls.status_criacao_plano_invalido = res.status_code

    def test_nutricionista_cria_plano_com_id_aluno_inexistente(self):
        assert self.status_criacao_plano_invalido in (400, 404)

    def test_personal_nao_pode_criar_plano_alimentar(self):
        res = self.client.post("/planos/", json={
            "id_aluno": 1,
            "refeicoes": []
        }, headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code == 403

    def test_aluno_nao_pode_adicionar_exercicio_em_treino(self):
        res = self.client.post("/treinos/", json={
            "id_aluno": 1,
            "nome_treino": "Treino Aluno",
            "exercicios": []
        }, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_personal_registra_treino_para_id_invalido(self):
        res = self.client.post("/registrostreino/", json={
            "id_treino": 9999,
            "id_aluno": 9999,
            "observacoes": "Treino com id inválido",
            "cargas": []
        }, headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code in (400, 404)
