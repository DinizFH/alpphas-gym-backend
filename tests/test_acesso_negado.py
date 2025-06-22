import os
os.environ["FLASK_ENV"] = "testing"

from app import create_app

class TestAcessoNegado:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuário aluno
        res_aluno = cls.client.post("/auth/register", json={
            "nome": "Aluno Teste",
            "email": "aluno@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        cls.id_aluno = res_aluno.get_json().get("id_usuario")

        # Criar usuário personal
        res_personal = cls.client.post("/auth/register", json={
            "nome": "Personal Teste",
            "email": "personal@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF123"
        })
        cls.id_personal = res_personal.get_json().get("id_usuario")

        # Criar usuário nutricionista
        res_nutri = cls.client.post("/auth/register", json={
            "nome": "Nutricionista Teste",
            "email": "nutri@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN456"
        })
        cls.id_nutri = res_nutri.get_json().get("id_usuario")

        # Logins
        cls.token_aluno = cls.client.post("/auth/login", json={"email": "aluno@teste.com", "senha": "123456"}).get_json()["access_token"]
        cls.token_personal = cls.client.post("/auth/login", json={"email": "personal@teste.com", "senha": "123456"}).get_json()["access_token"]
        cls.token_nutri = cls.client.post("/auth/login", json={"email": "nutri@teste.com", "senha": "123456"}).get_json()["access_token"]

        # Criar exercício
        res_exercicio = cls.client.post("/exercicios/", json={
            "nome": "Supino Reto",
            "grupo_muscular": "Peito",
            "observacoes": "Exercício básico de peito",
            "video": "https://youtube.com/supino"
        }, headers={"Authorization": f"Bearer {cls.token_personal}"})
        cls.id_exercicio = res_exercicio.get_json().get("id_exercicio", 1)

        # Criar treino
        res_treino = cls.client.post("/treinos/", json={
            "id_aluno": cls.id_aluno,
            "nome": "Treino A",
            "exercicios": [
                {"id_exercicio": cls.id_exercicio, "series": 3, "repeticoes": 12, "observacoes": "Foco"}
            ]
        }, headers={"Authorization": f"Bearer {cls.token_personal}"})
        cls.id_treino = res_treino.get_json().get("id_treino", 1)

        # Criar plano alimentar
        res_plano = cls.client.post("/planos/", json={
            "id_aluno": cls.id_aluno,
            "refeicoes": [
                {
                    "titulo": "Café da Manhã",
                    "calorias_estimadas": 300,
                    "alimentos": [
                        {"nome": "Ovo", "quantidade": "2"},
                        {"nome": "Pão Integral", "quantidade": "1 fatia"}
                    ]
                }
            ]
        }, headers={"Authorization": f"Bearer {cls.token_nutri}"})

        # Debug (remova após confirmar)
        print("RES_PLANO:", res_plano.status_code, res_plano.get_json())

        # Obter ID do plano
        if res_plano.status_code == 201:
            cls.id_plano = res_plano.get_json().get("id_plano")
        else:
            cls.id_plano = 1

    # === GERAL ===
    def test_sem_token_em_rota_protegida(self):
        res = self.client.get("/usuarios/perfil")
        assert res.status_code == 401

    # === AVALIAÇÕES ===
    def test_aluno_nao_pode_criar_avaliacao(self):
        res = self.client.post("/avaliacoes/", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_aluno_nao_pode_editar_avaliacao(self):
        res = self.client.put("/avaliacoes/1", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code in [403, 404]

    def test_aluno_nao_pode_excluir_avaliacao(self):
        res = self.client.delete("/avaliacoes/1", headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code in [403, 404]

    def test_sem_token_em_avaliacoes(self):
        res = self.client.get("/avaliacoes/")
        assert res.status_code == 401

    # === AGENDAMENTOS ===
    def test_aluno_nao_pode_criar_agendamento(self):
        res = self.client.post("/agendamentos/", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_sem_token_em_agendamentos(self):
        res = self.client.get("/agendamentos/")
        assert res.status_code == 401

    # === EXERCÍCIOS ===
    def test_aluno_nao_pode_criar_exercicio(self):
        res = self.client.post("/exercicios/", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_nutri_nao_pode_criar_exercicio(self):
        res = self.client.post("/exercicios/", json={}, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code == 403

    def test_nutri_nao_pode_editar_exercicio(self):
        res = self.client.put("/exercicios/1", json={}, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code in [403, 404]

    def test_nutri_nao_pode_excluir_exercicio(self):
        res = self.client.delete("/exercicios/1", headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code in [403, 404]

    def test_sem_token_em_exercicios(self):
        res = self.client.get("/exercicios/")
        assert res.status_code == 401

    # === PLANOS ALIMENTARES ===
    def test_personal_nao_pode_criar_plano(self):
        res = self.client.post("/planos/", json={}, headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code == 403

    def test_aluno_nao_pode_criar_plano(self):
        res = self.client.post("/planos/", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_aluno_nao_pode_excluir_plano(self):
        res = self.client.delete("/planos/1", headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code in [403, 404]

    def test_personal_nao_pode_enviar_plano_whatsapp(self):
        res = self.client.post(f"/planos/{self.id_plano}/enviar-whatsapp", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code in [403, 404]

    def test_aluno_nao_pode_enviar_plano_email(self):
        res = self.client.post(f"/planos/{self.id_plano}/email", headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code in [403, 404]

    def test_personal_nao_pode_enviar_plano_email(self):
        res = self.client.post(f"/planos/{self.id_plano}/email", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code in [403, 404]

    def test_sem_token_em_planos(self):
        res = self.client.get("/planos/")
        assert res.status_code == 401

    # === REGISTRO DE TREINO ===
    def test_nutri_nao_pode_criar_registro(self):
        payload = {
            "id_treino": self.id_treino,
            "cargas": [{"id_exercicio": self.id_exercicio, "carga": 50}],
            "observacoes": "Teste"
        }
        res = self.client.post("/registrostreino/", json=payload, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code == 403

    def test_nutri_nao_pode_excluir_registro(self):
        res = self.client.delete("/registrostreino/1", headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code in [403, 404]

    def test_sem_token_em_registrostreino(self):
        res = self.client.get("/registrostreino/")
        assert res.status_code == 401

    # === TREINOS ===
    def test_aluno_nao_pode_criar_treino(self):
        res = self.client.post("/treinos/", json={}, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 403

    def test_aluno_nao_pode_excluir_treino(self):
        res = self.client.delete("/treinos/1", headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code in [403, 404]

    def test_nutri_nao_pode_excluir_treino(self):
        res = self.client.delete("/treinos/1", headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code in [403, 404]

    def test_nutri_nao_pode_editar_treino(self):
        res = self.client.put("/treinos/1", json={}, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code in [403, 404]

    def test_nutri_nao_pode_criar_treino(self):
        res = self.client.post("/treinos/", json={}, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code == 403

    def test_sem_token_em_treinos(self):
        res = self.client.get("/treinos/aluno")
        assert res.status_code == 401
