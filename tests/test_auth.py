import pytest
import uuid

@pytest.mark.usefixtures("client")
class TestAuth:

    def gerar_email(self, prefixo):
        return f"{prefixo}_{uuid.uuid4().hex[:6]}@teste.com"

    def test_registro_valido_aluno(self, client):
        email = self.gerar_email("aluno")
        res = client.post("/auth/register", json={
            "nome": "Aluno Teste",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        assert res.status_code == 201
        assert "Usuário registrado com sucesso" in res.get_json()["msg"]

    def test_registro_valido_personal(self, client):
        email = self.gerar_email("personal")
        res = client.post("/auth/register", json={
            "nome": "Personal Teste",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "123456-PB"
        })
        assert res.status_code == 201
        assert "Usuário registrado com sucesso" in res.get_json()["msg"]

    def test_registro_valido_nutricionista(self, client):
        email = self.gerar_email("nutri")
        res = client.post("/auth/register", json={
            "nome": "Nutri Teste",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "nutricionista",
            "crn": "78910-PE"
        })
        assert res.status_code == 201
        assert "Usuário registrado com sucesso" in res.get_json()["msg"]

    def test_registro_com_email_repetido(self, client):
        email = self.gerar_email("repetido")
        client.post("/auth/register", json={
            "nome": "Teste",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res = client.post("/auth/register", json={
            "nome": "Outro",
            "email": email,
            "senha": "abcdef",
            "tipo_usuario": "aluno"
        })
        assert res.status_code == 400
        assert "E-mail já registrado" in res.get_json()["msg"]

    def test_registro_tipo_invalido(self, client):
        email = self.gerar_email("invalido")
        res = client.post("/auth/register", json={
            "nome": "Invalido",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "admin"
        })
        assert res.status_code == 400
        assert "Tipo de usuário inválido" in res.get_json()["msg"]

    def test_registro_campos_faltando(self, client):
        res = client.post("/auth/register", json={
            "nome": "Sem Email",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        assert res.status_code == 400

    def test_login_valido(self, client):
        email = self.gerar_email("login")
        client.post("/auth/register", json={
            "nome": "Login User",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res = client.post("/auth/login", json={
            "email": email,
            "senha": "123456"
        })
        assert res.status_code == 200
        assert "access_token" in res.get_json()

    def test_login_senha_errada(self, client):
        email = self.gerar_email("senhaerrada")
        client.post("/auth/register", json={
            "nome": "Senha Errada",
            "email": email,
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res = client.post("/auth/login", json={
            "email": email,
            "senha": "errada"
        })
        assert res.status_code == 401

    def test_login_usuario_inexistente(self, client):
        email = self.gerar_email("inexistente")
        res = client.post("/auth/login", json={
            "email": email,
            "senha": "123456"
        })
        assert res.status_code == 401
