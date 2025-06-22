import pytest
from datetime import datetime, timedelta
from app import create_app
import uuid

class TestAgendamentos:

    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Gerar e-mails únicos
        cls.email_personal = f"personalagenda_{uuid.uuid4().hex[:6]}@teste.com"
        cls.email_aluno = f"alunoagenda_{uuid.uuid4().hex[:6]}@teste.com"

        # Registrar personal
        cls.client.post("/auth/register", json={
            "nome": "Personal Agenda",
            "email": cls.email_personal,
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "12345-PB"
        })

        # Registrar aluno
        cls.client.post("/auth/register", json={
            "nome": "Aluno Agendado",
            "email": cls.email_aluno,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        # Login personal
        res_login = cls.client.post("/auth/login", json={
            "email": cls.email_personal,
            "senha": "123456"
        })
        cls.token_personal = res_login.get_json()["access_token"]

        # Buscar aluno
        res_busca = cls.client.get("/avaliacoes/buscar-aluno?nome=Aluno", headers={"Authorization": f"Bearer {cls.token_personal}"})
        cls.id_aluno = res_busca.get_json()[0]["id_usuario"]

        # Criar agendamento base
        inicio = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        fim = (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        res_create = cls.client.post("/agendamentos/", headers={"Authorization": f"Bearer {cls.token_personal}"}, json={
            "id_aluno": cls.id_aluno,
            "tipo_agendamento": "treino",
            "data_hora_inicio": inicio,
            "data_hora_fim": fim,
            "observacoes": "Teste para editar e buscar"
        })
        cls.id_agendamento = res_create.get_json()["id_agendamento"]

    def test_01_criar_listar_cancelar_agendamento(self):
        inicio = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        fim = (datetime.now() + timedelta(days=2, hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        res_create = self.client.post("/agendamentos/", headers={"Authorization": f"Bearer {self.token_personal}"}, json={
            "id_aluno": self.id_aluno,
            "tipo_agendamento": "treino",
            "data_hora_inicio": inicio,
            "data_hora_fim": fim,
            "observacoes": "Teste funcional"
        })
        assert res_create.status_code == 201
        id_agendamento = res_create.get_json()["id_agendamento"]

        res_list = self.client.get("/agendamentos/", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res_list.status_code == 200
        lista = res_list.get_json()
        assert any(a["id_agendamento"] == id_agendamento for a in lista)

        res_cancel = self.client.delete(f"/agendamentos/{id_agendamento}", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res_cancel.status_code == 200
        assert "cancelado" in res_cancel.get_json()["msg"].lower()

    def test_02_aluno_nao_pode_criar_agendamento(self):
        email_aluno = f"bloqueado_{uuid.uuid4().hex[:6]}@teste.com"

        self.client.post("/auth/register", json={
            "nome": "Aluno Bloqueado",
            "email": email_aluno,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })

        res_login = self.client.post("/auth/login", json={
            "email": email_aluno,
            "senha": "123456"
        })
        token = res_login.get_json()["access_token"]

        res = self.client.post("/agendamentos/", headers={"Authorization": f"Bearer {token}"}, json={
            "id_aluno": self.id_aluno,
            "tipo_agendamento": "Tentativa",
            "data_hora_inicio": "2030-01-01 10:00:00",
            "data_hora_fim": "2030-01-01 11:00:00",
            "observacoes": "Tentativa não permitida"
        })
        assert res.status_code == 403
        assert "apenas personal ou nutricionista" in res.get_json()["msg"].lower()

    def test_03_obter_agendamento_por_id(self):
        res_get = self.client.get(f"/agendamentos/{self.id_agendamento}", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res_get.status_code == 200
        dados = res_get.get_json()
        assert dados["id_agendamento"] == self.id_agendamento
        assert dados["nome_aluno"].lower().startswith("aluno")
        assert dados["nome_profissional"].lower().startswith("personal")

    def test_04_editar_agendamento(self):
        novo_inicio = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        novo_fim = (datetime.now() + timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        res_put = self.client.put(f"/agendamentos/{self.id_agendamento}", headers={"Authorization": f"Bearer {self.token_personal}"}, json={
            "data_hora_inicio": novo_inicio,
            "data_hora_fim": novo_fim,
            "status": "concluído",
            "observacoes": "Alterado para concluído"
        })
        assert res_put.status_code == 200
        assert "atualizado" in res_put.get_json()["msg"].lower()

    def test_05_obter_agendamento_inexistente(self):
        res = self.client.get("/agendamentos/999999", headers={"Authorization": f"Bearer {self.token_personal}"})
        assert res.status_code == 404
