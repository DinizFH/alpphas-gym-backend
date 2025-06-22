import pytest
from app import create_app

class TestRegistroTreino:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuários
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

        # Login e tokens
        cls.token_personal = cls.client.post("/auth/login", json={
            "email": "personal@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        cls.token_aluno = cls.client.post("/auth/login", json={
            "email": "aluno@teste.com", "senha": "123456"
        }).get_json()["access_token"]

        # Obter ID do aluno
        perfil_aluno = cls.client.get("/usuarios/perfil", headers={
            "Authorization": f"Bearer {cls.token_aluno}"
        }).get_json()
        cls.id_aluno = perfil_aluno["id_usuario"]

        # Criar exercício
        res_ex = cls.client.post("/exercicios/", json={
            "nome": "Supino Reto",
            "grupo_muscular": "Peito",
            "observacoes": "3x10",
            "video": ""
        }, headers={"Authorization": f"Bearer {cls.token_personal}"})
        assert res_ex.status_code == 201, f"Erro ao criar exercício: {res_ex.data}"

        # Buscar ID do exercício
        res_lista = cls.client.get("/exercicios/?nome=Supino", headers={
            "Authorization": f"Bearer {cls.token_personal}"
        })
        data = res_lista.get_json()
        assert isinstance(data, list) and len(data) > 0, "Exercício não encontrado"
        cls.id_exercicio = data[0]["id_exercicio"]

        # Criar treino
        res_treino = cls.client.post("/treinos/", json={
            "id_aluno": cls.id_aluno,
            "nome_treino": "Treino A",
            "objetivo": "Hipertrofia",
            "exercicios": [
                {
                    "id_exercicio": cls.id_exercicio,
                    "series": 3,
                    "repeticoes": 10,
                    "observacoes": ""
                }
            ]
        }, headers={"Authorization": f"Bearer {cls.token_personal}"})
        assert res_treino.status_code == 201, f"Erro ao criar treino: {res_treino.data}"
        cls.id_treino = res_treino.get_json()["id_treino"]

    def test_01_criar_registro_treino(self):
        res = self.client.post("/registrostreino/", json={
            "id_treino": self.__class__.id_treino,
            "id_aluno": self.__class__.id_aluno,
            "observacoes": "Primeiro registro",
            "cargas": [
                {"id_exercicio": self.__class__.id_exercicio, "carga": 40}
            ]
        }, headers={"Authorization": f"Bearer {self.__class__.token_personal}"})
        assert res.status_code == 201, f"Erro ao criar registro: {res.data}"
        self.__class__.id_registro = res.get_json()["id_registro"]

    def test_02_listar_registros(self):
        res = self.client.get("/registrostreino/", headers={
            "Authorization": f"Bearer {self.__class__.token_personal}"})
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_03_listar_meus_registros(self):
        res = self.client.get("/registrostreino/meus", headers={
            "Authorization": f"Bearer {self.__class__.token_aluno}"})
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_04_obter_registro_por_id(self):
        res = self.client.get(f"/registrostreino/{self.__class__.id_registro}", headers={
            "Authorization": f"Bearer {self.__class__.token_aluno}"})
        assert res.status_code == 200
        assert "exercicios" in res.get_json()

    def test_05_atualizar_registro(self):
        res = self.client.put(f"/registrostreino/{self.__class__.id_registro}", json={
            "observacoes": "Atualizado",
            "cargas": [
                {"id_exercicio": self.__class__.id_exercicio, "carga": 45}
            ]
        }, headers={"Authorization": f"Bearer {self.__class__.token_aluno}"})
        assert res.status_code == 200

    def test_06_buscar_registros_por_nome(self):
        res = self.client.get("/registrostreino/aluno?nome=Aluno", headers={
            "Authorization": f"Bearer {self.__class__.token_personal}"})
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_07_excluir_registro(self):
        res = self.client.delete(f"/registrostreino/{self.__class__.id_registro}", headers={
            "Authorization": f"Bearer {self.__class__.token_aluno}"})
        assert res.status_code == 200
