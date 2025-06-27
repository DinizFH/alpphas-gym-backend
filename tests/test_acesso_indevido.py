import pytest
from app import create_app
from flask import json


class TestAcessoIndevido:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Registrar Personal 1
        cls.client.post("/auth/register", json={
            "nome": "Personal 1",
            "email": "personal1@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF001"
        })

        # Registrar Nutricionista 1
        cls.client.post("/auth/register", json={
            "nome": "Nutricionista 1",
            "email": "nutri1@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN001"
        })

        # Registrar Aluno 1
        cls.client.post("/auth/register", json={
            "nome": "Aluno 1",
            "email": "aluno1@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Registrar Aluno 2
        cls.client.post("/auth/register", json={
            "nome": "Aluno 2",
            "email": "aluno2@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login
        cls.token_personal1 = cls.client.post("/auth/login", json={"email": "personal1@teste.com", "senha": "123456"}).get_json()["access_token"]
        cls.token_nutri1 = cls.client.post("/auth/login", json={"email": "nutri1@teste.com", "senha": "123456"}).get_json()["access_token"]
        cls.token_aluno1 = cls.client.post("/auth/login", json={"email": "aluno1@teste.com", "senha": "123456"}).get_json()["access_token"]
        cls.token_aluno2 = cls.client.post("/auth/login", json={"email": "aluno2@teste.com", "senha": "123456"}).get_json()["access_token"]

        perfil_aluno1 = cls.client.get("/usuarios/perfil", headers={"Authorization": f"Bearer {cls.token_aluno1}"}).get_json()
        cls.id_aluno1 = perfil_aluno1["id_usuario"]

        perfil_aluno2 = cls.client.get("/usuarios/perfil", headers={"Authorization": f"Bearer {cls.token_aluno2}"}).get_json()
        cls.id_aluno2 = perfil_aluno2["id_usuario"]

    def test_01_aluno_nao_pode_criar_agendamento(self):
        res = self.client.post("/agendamentos/", json={
            "id_aluno": self.id_aluno1,
            "id_profissional": 999,
            "tipo_agendamento": "Treino",
            "data_hora_inicio": "2030-01-01T10:00:00",
            "data_hora_fim": "2030-01-01T11:00:00"
        }, headers={"Authorization": f"Bearer {self.token_aluno1}"})
        assert res.status_code == 403

    def test_02_aluno_nao_pode_criar_avaliacao(self):
        res = self.client.post("/avaliacoes/", json={
            "id_aluno": self.id_aluno1,
            "peso": 70,
            "altura": 1.75,
            "idade": 25,
            "dobra_triceps": 10,
            "dobra_subescapular": 12,
            "dobra_biceps": 8,
            "dobra_axilar_media": 9,
            "dobra_supra_iliaca": 11,
            "braco_d_contraido": 30,
            "braco_e_contraido": 29,
            "ombro": 40,
            "torax": 90,
            "cintura": 80,
            "abdomen": 85,
            "quadril": 95,
            "coxa_d": 60,
            "coxa_e": 59,
            "panturrilha_d": 35,
            "panturrilha_e": 34,
            "observacoes": "Teste"
        }, headers={"Authorization": f"Bearer {self.token_aluno1}"})
        assert res.status_code == 403

    def test_03_aluno_nao_pode_criar_treino(self):
        res = self.client.post("/treinos/", json={
            "id_aluno": self.id_aluno1,
            "nome_treino": "Treino A",
            "objetivo": "Hipertrofia",
            "exercicios": []
        }, headers={"Authorization": f"Bearer {self.token_aluno1}"})
        assert res.status_code == 403

    def test_04_aluno_nao_pode_criar_plano_alimentar(self):
        res = self.client.post("/planos/", json={
            "id_aluno": self.id_aluno1,
            "titulo": "Plano Teste",
            "descricao_geral": "Plano criado para teste",
            "refeicoes": []
        }, headers={"Authorization": f"Bearer {self.token_aluno1}"})
        assert res.status_code == 403

    def test_05_aluno_nao_pode_ver_registros_de_outro_aluno(self):
        res = self.client.get(f"/registrostreino/aluno?id_aluno={self.id_aluno2}", headers={
            "Authorization": f"Bearer {self.token_aluno1}"
        })
        assert res.status_code == 403

    def test_06_personal_nao_pode_excluir_avaliacao_de_outro(self):
        res = self.client.post("/avaliacoes/", json={
            "id_aluno": self.id_aluno1,
            "peso": 70,
            "altura": 1.75,
            "idade": 25,
            "dobra_peitoral": 10,
            "dobra_triceps": 10,
            "dobra_subescapular": 12,
            "dobra_biceps": 8,
            "dobra_axilar_media": 9,
            "dobra_supra_iliaca": 11,
            "braco_d_contraido": 30,
            "braco_e_contraido": 29,
            "ombro": 40,
            "torax": 90,
            "cintura": 80,
            "abdomen": 85,
            "quadril": 95,
            "coxa_d": 60,
            "coxa_e": 59,
            "panturrilha_d": 35,
            "panturrilha_e": 34,
            "observacoes": "Teste"
        }, headers={"Authorization": f"Bearer {self.token_personal1}"})
        assert res.status_code == 201
        id_avaliacao = res.get_json().get("id_avaliacao", 1)
        res_excluir = self.client.delete(f"/avaliacoes/{id_avaliacao}", headers={
            "Authorization": f"Bearer {self.token_nutri1}"
        })
        assert res_excluir.status_code in [403, 404]

    def test_07_nutri_nao_pode_editar_plano_de_outro(self):
        res = self.client.post("/planos/", json={
            "id_aluno": self.id_aluno1,
            "titulo": "Plano Teste",
            "descricao_geral": "Plano criado para teste",
            "refeicoes": [
                {
                    "titulo": "Café da manhã",
                    "calorias_estimadas": 300,
                    "alimentos": [
                        {"nome": "Pão integral", "peso": 50},
                        {"nome": "Ovo cozido", "peso": 60}
                    ]
                }
            ]
        }, headers={"Authorization": f"Bearer {self.token_nutri1}"})
        assert res.status_code == 201
        id_plano = res.get_json().get("id_plano", 1)
        res_editar = self.client.put(f"/planos/{id_plano}", json={
            "descricao_geral": "Alteração indevida"
        }, headers={"Authorization": f"Bearer {self.token_personal1}"})
        assert res_editar.status_code == 403

    def test_08_aluno_nao_pode_excluir_treino(self):
        res_excluir = self.client.delete(f"/treinos/999", headers={
            "Authorization": f"Bearer {self.token_aluno1}"
        })
        assert res_excluir.status_code in [403, 404]

    def test_09_aluno_nao_pode_excluir_avaliacao(self):
        res_excluir = self.client.delete(f"/avaliacoes/999", headers={
            "Authorization": f"Bearer {self.token_aluno1}"
        })
        assert res_excluir.status_code in [403, 404]

    def test_10_aluno_nao_pode_excluir_plano(self):
        res_excluir = self.client.delete(f"/planos/999", headers={
            "Authorization": f"Bearer {self.token_aluno1}"
        })
        assert res_excluir.status_code in [403, 404]
