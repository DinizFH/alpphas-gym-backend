import pytest

@pytest.mark.usefixtures("client")
class TestAvaliacoes:
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.client = client

        # Criar profissional
        self.client.post("/auth/register", json={
            "nome": "Profissional Teste",
            "email": "prof@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "CREF123"
        })
        token_p = self.client.post("/auth/login", json={
            "email": "prof@teste.com", "senha": "123456"
        }).get_json()["access_token"]
        self.headers_prof = {"Authorization": f"Bearer {token_p}"}

        # Criar aluno
        self.client.post("/auth/register", json={
            "nome": "Aluno Teste",
            "email": "aluno@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        token_a = self.client.post("/auth/login", json={
            "email": "aluno@teste.com", "senha": "123456"
        }).get_json()["access_token"]
        self.headers_aluno = {"Authorization": f"Bearer {token_a}"}
        perfil = self.client.get("/usuarios/perfil", headers=self.headers_aluno)
        self.id_aluno = perfil.get_json()["id_usuario"]

        # Criar avaliação
        payload = {
            "id_aluno": self.id_aluno,
            "idade": 25,
            "peso": 75.0,
            "altura": 1.75,
            "dobra_peitoral": 10,
            "dobra_triceps": 12,
            "dobra_subescapular": 14,
            "dobra_biceps": 8,
            "dobra_axilar_media": 10,
            "dobra_supra_iliaca": 9,
            "pescoco": 38,
            "ombro": 110,
            "torax": 100,
            "cintura": 85,
            "abdomen": 88,
            "quadril": 95,
            "braco_d": 35,
            "braco_e": 34,
            "braco_d_contraido": 37,
            "braco_e_contraido": 36,
            "antebraco_d": 30,
            "antebraco_e": 29,
            "coxa_d": 60,
            "coxa_e": 59,
            "panturrilha_d": 38,
            "panturrilha_e": 37,
            "observacoes": "Avaliação inicial"
        }
        self.client.post("/avaliacoes/", headers=self.headers_prof, json=payload)

        res = self.client.get("/avaliacoes/", headers=self.headers_prof)
        data = res.get_json()
        self.id_avaliacao = data[0]["id_avaliacao"]

    def test_01_listar_avaliacoes(self):
        res = self.client.get("/avaliacoes/", headers=self.headers_prof)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_02_obter_avaliacao(self):
        res = self.client.get(f"/avaliacoes/{self.id_avaliacao}", headers=self.headers_prof)
        assert res.status_code == 200
        assert "nome_aluno" in res.get_json()

    def test_03_editar_avaliacao(self):
        dados = self.client.get(f"/avaliacoes/{self.id_avaliacao}", headers=self.headers_prof).get_json()
        dados.update({
            "peso": 78.0,
            "observacoes": "Revisado"
        })
        res = self.client.put(f"/avaliacoes/{self.id_avaliacao}", headers=self.headers_prof, json=dados)
        assert res.status_code == 200

    def test_04_excluir_avaliacao(self):
        res = self.client.delete(f"/avaliacoes/{self.id_avaliacao}", headers=self.headers_prof)
        assert res.status_code == 200
