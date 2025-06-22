import pytest
from app import create_app
import random

class TestFluxoCompleto:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # E-mails únicos por execução
        sufixo = str(random.randint(1000, 9999))
        cls.email_nutri = f"nutrifluxo{sufixo}@teste.com"
        cls.email_personal = f"personalfluxo{sufixo}@teste.com"
        cls.email_aluno = f"alunofluxo{sufixo}@teste.com"

        # Criar nutricionista
        cls.client.post("/auth/register", json={
            "nome": "Nutricionista Fluxo",
            "email": cls.email_nutri,
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": f"CRN{sufixo}"
        })

        # Criar personal
        cls.client.post("/auth/register", json={
            "nome": "Personal Fluxo",
            "email": cls.email_personal,
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": f"CREF{sufixo}"
        })

        # Criar aluno
        cls.client.post("/auth/register", json={
            "nome": "Aluno Fluxo",
            "email": cls.email_aluno,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login
        cls.token_nutri = cls.client.post("/auth/login", json={
            "email": cls.email_nutri, "senha": "123456"
        }).get_json()["access_token"]

        cls.token_personal = cls.client.post("/auth/login", json={
            "email": cls.email_personal, "senha": "123456"
        }).get_json()["access_token"]

        cls.token_aluno = cls.client.post("/auth/login", json={
            "email": cls.email_aluno, "senha": "123456"
        }).get_json()["access_token"]

        cls.headers_nutri = {"Authorization": f"Bearer {cls.token_nutri}"}
        cls.headers_personal = {"Authorization": f"Bearer {cls.token_personal}"}
        cls.headers_aluno = {"Authorization": f"Bearer {cls.token_aluno}"}

        # Buscar ID do aluno
        res_alunos = cls.client.get("/usuarios/alunos", headers=cls.headers_personal)
        cls.id_aluno = res_alunos.get_json()[0]["id_usuario"]

        # Criar exercício
        res_exercicio = cls.client.post("/exercicios/", headers=cls.headers_personal, json={
            "nome": f"Agachamento {sufixo}",
            "grupo_muscular": "Pernas",
            "observacoes": "Agachar até 90º",
            "video": ""
        })
        cls.id_exercicio = res_exercicio.get_json().get("id_exercicio")

        # Criar treino
        res_treino = cls.client.post("/treinos/", headers=cls.headers_personal, json={
            "id_aluno": cls.id_aluno,
            "nome_treino": f"Treino Completo {sufixo}",
            "exercicios": [
                {"id_exercicio": cls.id_exercicio, "series": 3, "repeticoes": 12, "observacoes": "Carga leve"}
            ]
        })
        cls.id_treino = res_treino.get_json().get("id")

        # Criar avaliação física
        cls.client.post("/avaliacoes/", headers=cls.headers_personal, json={
            "id_aluno": cls.id_aluno,
            "peso": 70,
            "altura": 1.75,
            "idade": 30,
            "dobra_triceps": 12,
            "dobra_subescapular": 10,
            "dobra_biceps": 8,
            "dobra_axilar_media": 11,
            "dobra_supra_iliaca": 9
        })

        # Criar plano alimentar
        res_plano = cls.client.post("/planos/", headers=cls.headers_nutri, json={
            "id_aluno": cls.id_aluno,
            "refeicoes": [
                {
                    "titulo": "Café da Manhã",
                    "calorias_estimadas": 350,
                    "alimentos": [
                        {"nome": "Ovos", "peso": "120g"},
                        {"nome": "Frutas", "peso": "150g"}
                    ]
                }
            ]
        })
        cls.id_plano = res_plano.get_json().get("id_plano")

        # Criar registro de treino
        cls.client.post("/registrostreino/", headers=cls.headers_aluno, json={
            "id_treino": cls.id_treino,
            "observacoes": "Execução completa",
            "cargas": [{"id_exercicio": cls.id_exercicio, "carga": 40}]
        })

    def test_01_exportar_pdf(self):
        res = self.client.get(f"/planos/{self.id_plano}/pdf", headers=self.headers_nutri)
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert res.data.startswith(b"%PDF")
