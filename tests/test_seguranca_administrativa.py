import pytest
from app import create_app
from app.extensions.db import get_db


class TestSegurancaAdministrativa:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar usuários
        cls.client.post("/auth/register", json={
            "nome": "Nutricionista Seg",
            "email": "nutri_seg@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN789"
        })

        cls.client.post("/auth/register", json={
            "nome": "Aluno Seg",
            "email": "aluno_seg@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Ativar o aluno manualmente no banco de dados
        with cls.app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuarios SET ativo = TRUE
                    WHERE email = %s
                """, ("aluno_seg@teste.com",))
            db.commit()

        # Login dos usuários
        res_nutri = cls.client.post("/auth/login", json={
            "email": "nutri_seg@teste.com", "senha": "123456"
        })
        res_aluno = cls.client.post("/auth/login", json={
            "email": "aluno_seg@teste.com", "senha": "123456"
        })

        try:
            cls.token_nutri = res_nutri.get_json()["access_token"]
            cls.token_aluno = res_aluno.get_json()["access_token"]
        except Exception:
            print("Erro ao obter tokens de acesso")
            print("nutri:", res_nutri.status_code, res_nutri.data)
            print("aluno:", res_aluno.status_code, res_aluno.data)
            raise

    def test_nutricionista_nao_pode_virar_personal(self):
        res = self.client.put("/usuarios/editar", json={
            "tipo_usuario": "personal"
        }, headers={"Authorization": f"Bearer {self.token_nutri}"})
        assert res.status_code == 400  # Espera falha

    def test_aluno_nao_pode_virar_nutricionista(self):
        res = self.client.put("/usuarios/editar", json={
            "tipo_usuario": "nutricionista"
        }, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 400  # Espera falha

    def test_aluno_nao_pode_alterar_ativo_ou_perfil_completo(self):
        with self.app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", ("aluno_seg@teste.com",))
                id_usuario = cursor.fetchone()["id_usuario"]

        res = self.client.put("/usuarios/editar", json={
            "nome": "Aluno Invasor",
            "ativo": False,
            "perfil_completo": True
        }, headers={"Authorization": f"Bearer {self.token_aluno}"})
        assert res.status_code == 200  # Nome pode ser editado

        with self.app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT ativo, perfil_completo FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                dados = cursor.fetchone()
                assert dados["ativo"] == 1  # Continua ativo
                assert dados["perfil_completo"] == 0  # Continua incompleto
