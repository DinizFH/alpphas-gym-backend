import pytest

@pytest.mark.usefixtures("client")
class TestUsuarios:

    def test_obter_perfil(self, client):
        # Registro e login
        client.post("/auth/register", json={
            "nome": "João Perfil",
            "email": "joaoperfil@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res_login = client.post("/auth/login", json={
            "email": "joaoperfil@teste.com",
            "senha": "123456"
        })
        token = res_login.get_json()["access_token"]

        res = client.get("/usuarios/perfil", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["email"] == "joaoperfil@teste.com"
        assert data["tipo_usuario"] == "aluno"

    def test_editar_usuario(self, client):
        # Registro e login
        client.post("/auth/register", json={
            "nome": "Joana",
            "email": "joana@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res_login = client.post("/auth/login", json={
            "email": "joana@teste.com",
            "senha": "123456"
        })
        token = res_login.get_json()["access_token"]

        # Atualizar dados
        res = client.put("/usuarios/editar", json={
            "nome": "Joana Silva",
            "telefone": "83999999999",
            "data_nascimento": "2000-01-01",
            "genero": "feminino"
        }, headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 200
        assert "Perfil atualizado com sucesso" in res.get_json()["msg"]

    def test_desativar_usuario(self, client):
        # Registro e login
        client.post("/auth/register", json={
            "nome": "Carlos",
            "email": "carlos@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        res_login = client.post("/auth/login", json={
            "email": "carlos@teste.com",
            "senha": "123456"
        })
        token = res_login.get_json()["access_token"]

        res = client.delete("/usuarios/desativar", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "Conta desativada com sucesso" in res.get_json()["msg"]

        # Tentar login novamente
        res_login2 = client.post("/auth/login", json={
            "email": "carlos@teste.com",
            "senha": "123456"
        })
        assert res_login2.status_code == 401
from io import BytesIO

def test_completar_perfil_com_foto(client):
    # Registro e login
    client.post("/auth/register", json={
        "nome": "Perfil Completo",
        "email": "completo@teste.com",
        "senha": "123456",
        "tipo_usuario": "aluno"
    })
    res_login = client.post("/auth/login", json={
        "email": "completo@teste.com",
        "senha": "123456"
    })
    token = res_login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Completar perfil
    data = {
        "cpf": "12345678900",
        "data_nascimento": "2000-01-01",
        "endereco": "Rua Teste",
        "telefone": "67999999999",
        "whatsapp": "5567999999999"
    }
    fake_image = (BytesIO(b"fake image data"), "foto.jpg")
    res = client.put("/usuarios/completar", headers=headers, data={
        **data,
        "foto_perfil": fake_image
    }, content_type="multipart/form-data")

    assert res.status_code == 200
    assert "completado" in res.get_json()["msg"].lower()


def test_listar_alunos_para_registro(client):
    # Registrar aluno
    client.post("/auth/register", json={
        "nome": "Aluno Registro",
        "email": "registro@teste.com",
        "senha": "123456",
        "tipo_usuario": "aluno"
    })
    res_login = client.post("/auth/login", json={
        "email": "registro@teste.com",
        "senha": "123456"
    })
    token = res_login.get_json()["access_token"]

    # Chamar rota
    res = client.get("/usuarios/alunos", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    alunos = res.get_json()
    assert any("Aluno Registro" in aluno["nome"] for aluno in alunos)
