import pytest
from app import create_app

class TestExportarPDF:
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Criar nutricionista e aluno
        cls.client.post("/auth/register", json={
            "nome": "Nutri PDF",
            "email": "nutripdf@teste.com",
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "CRN999"
        })
        cls.client.post("/auth/register", json={
            "nome": "Aluno PDF",
            "email": "alunopdf@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login do nutricionista
        res_login = cls.client.post("/auth/login", json={
            "email": "nutripdf@teste.com", "senha": "123456"
        })
        cls.token_nutri = res_login.get_json()["access_token"]
        cls.headers_nutri = {"Authorization": f"Bearer {cls.token_nutri}"}

        # Buscar ID do aluno
        res_alunos = cls.client.get("/usuarios/alunos", headers=cls.headers_nutri)
        cls.id_aluno = res_alunos.get_json()[0]["id_usuario"]

        # Criar plano alimentar com campo 'peso' nos alimentos
        res_plano = cls.client.post("/planos/", headers=cls.headers_nutri, json={
            "id_aluno": cls.id_aluno,
            "refeicoes": [
                {
                    "titulo": "Café da Manhã",
                    "calorias_estimadas": 300,
                    "alimentos": [
                        {"nome": "Banana", "peso": "120g"},
                        {"nome": "Iogurte natural", "peso": "170g"}
                    ]
                }
            ]
        })

        json_plano = res_plano.get_json()
        assert res_plano.status_code in [200, 201], f"Erro ao criar plano: {json_plano}"
        cls.id_plano = json_plano.get("id_plano") or 1  # fallback se id não vier explicitamente

    def test_01_exportar_pdf_plano_alimentar(self):
        res = self.client.get(f"/planos/{self.id_plano}/pdf", headers=self.headers_nutri)
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert res.data.startswith(b"%PDF")
