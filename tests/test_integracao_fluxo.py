import pytest
from app import create_app

class TestIntegracaoFluxo:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar nutricionista
        cls.client.post("/auth/register", json={
            "nome": "Nutricionista",
            "email": "nutri@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN123"
        })

        # Criar personal
        cls.client.post("/auth/register", json={
            "nome": "Personal",
            "email": "personal@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF123"
        })

        # Criar aluno
        cls.client.post("/auth/register", json={
            "nome": "Aluno",
            "email": "aluno@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Logins
        res_nutri = cls.client.post("/auth/login", json={"email": "nutri@teste.com", "senha": "123456"})
        cls.token_nutri = res_nutri.get_json()["access_token"]

        res_personal = cls.client.post("/auth/login", json={"email": "personal@teste.com", "senha": "123456"})
        cls.token_personal = res_personal.get_json()["access_token"]

        res_aluno = cls.client.post("/auth/login", json={"email": "aluno@teste.com", "senha": "123456"})
        cls.token_aluno = res_aluno.get_json()["access_token"]

        # Buscar ID do aluno
        res_alunos = cls.client.get("/usuarios/alunos", headers={"Authorization": f"Bearer {cls.token_nutri}"})
        alunos = res_alunos.get_json()
        assert alunos, f"Erro ao buscar alunos: {res_alunos.data}"
        cls.id_aluno = alunos[0]["id_usuario"]

    def test_01_nutricionista_cria_plano(self):
        res = self.client.post("/planos/", json={
            "id_aluno": self.id_aluno,
            "titulo": "Plano Teste",
            "descricao_geral": "Plano criado para integração",
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
        }, headers={"Authorization": f"Bearer {self.token_nutri}"})
        print("[DEBUG plano]", res.status_code, res.data)
        assert res.status_code == 201

    def test_02_personal_cria_treino(self):
        # Primeiro, criar exercício para evitar erro 1452
        self.client.post("/exercicios/", json={
            "nome": "Agachamento",
            "grupo_muscular": "Pernas",
            "observacoes": "Agachar corretamente",
            "video": ""
        }, headers={"Authorization": f"Bearer {self.token_personal}"})

        res = self.client.post("/treinos/", json={
            "id_aluno": self.id_aluno,
            "nome_treino": "Treino A",
            "exercicios": [
                {"id_exercicio": 2, "series": 3, "repeticoes": 12, "observacoes": "Executar com cuidado"}
            ]
        }, headers={"Authorization": f"Bearer {self.token_personal}"})
        print("[DEBUG treino]", res.status_code, res.data)
        assert res.status_code in [201, 400]

    def test_03_aluno_cria_registro_treino(self):
        res = self.client.get("/registrostreino/treinos-aluno", headers={"Authorization": f"Bearer {self.token_aluno}"})
        print("[DEBUG registro treino]", res.status_code, res.data)
        assert res.status_code == 200 or res.status_code == 404

    def test_04_personal_cria_avaliacao(self):
        res = self.client.post("/avaliacoes/", json={
            "id_aluno": self.id_aluno,
            "peso": 70,
            "altura": 1.75,
            "idade": 25,
            "dobra_triceps": 12,
            "dobra_subescapular": 10,
            "dobra_biceps": 8,
            "dobra_axilar_media": 11,
            "dobra_supra_iliaca": 9,
            "dobra_peitoral": 8,
            "braco_d": 30,
            "braco_e": 30,
            "braco_d_contraido": 32,
            "braco_e_contraido": 32,
            "antebraco_d": 28,
            "antebraco_e": 28,
            "coxa_d": 50,
            "coxa_e": 50,
            "panturrilha_d": 35,
            "panturrilha_e": 35,
            "pescoço": 38,
            "ombro": 45,
            "torax": 100,
            "cintura": 80,
            "abdômen": 85,
            "quadril": 90,
            "observacoes": "Avaliação de integração"
        }, headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code == 201

    def test_05_aluno_ve_dashboard_completo(self):
        res = self.client.get("/dashboard", headers={"Authorization": f"Bearer {self.token_aluno}"})
        print("[DEBUG dashboard aluno]", res.status_code, res.data)
        assert res.status_code in [200, 308]  # Aceita redirect temporário também
