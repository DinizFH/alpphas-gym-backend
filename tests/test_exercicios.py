import pytest

@pytest.mark.usefixtures("client")
class TestExercicios:

    def test_personal_cria_lista_edita_exclui_exercicio(self, client):
        # Registrar e logar como personal
        client.post("/auth/register", json={
            "nome": "Personal Ex",
            "email": "ex@teste.com",
            "senha": "123456",
            "tipo_usuario": "personal",
            "cref": "12345"
        })
        login = client.post("/auth/login", json={
            "email": "ex@teste.com",
            "senha": "123456"
        })
        assert login.status_code == 200
        token = login.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Criar exercício
        res_create = client.post("/exercicios/", headers=headers, json={
            "nome": "Agachamento",
            "grupo_muscular": "Pernas",
            "observacoes": "Manter postura",
            "video": "http://exemplo.com/video"
        })
        assert res_create.status_code == 201

        # Buscar todos e pegar ID do exercício
        res_list = client.get("/exercicios/", headers=headers)
        assert res_list.status_code == 200
        lista = res_list.get_json()
        assert any(e["nome"] == "Agachamento" for e in lista)
        id_ex = next(e["id_exercicio"] for e in lista if e["nome"] == "Agachamento")

        # Obter exercício por ID
        res_get = client.get(f"/exercicios/{id_ex}", headers=headers)
        assert res_get.status_code == 200
        assert res_get.get_json()["nome"] == "Agachamento"

        # Editar exercício
        res_edit = client.put(f"/exercicios/{id_ex}", headers=headers, json={
            "nome": "Agachamento Livre",
            "grupo_muscular": "Pernas",
            "observacoes": "Atualizado",
            "video": "http://video.com"
        })
        assert res_edit.status_code == 200

        # Excluir exercício
        res_del = client.delete(f"/exercicios/{id_ex}", headers=headers)
        assert res_del.status_code == 200

    def test_aluno_nao_pode_criar_editar_excluir_exercicio(self, client):
        # Registrar e logar como aluno
        client.post("/auth/register", json={
            "nome": "Aluno Ex",
            "email": "alunoex@teste.com",
            "senha": "123456",
            "tipo_usuario": "aluno"
        })
        login = client.post("/auth/login", json={
            "email": "alunoex@teste.com",
            "senha": "123456"
        })
        assert login.status_code == 200
        token = login.get_json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Tentar criar exercício
        res_create = client.post("/exercicios/", headers=headers, json={
            "nome": "Remada",
            "grupo_muscular": "Costas",
            "observacoes": "",
            "video": ""
        })
        assert res_create.status_code == 403

        # Tentar editar exercício inexistente
        res_edit = client.put("/exercicios/999", headers=headers, json={
            "nome": "Remada Curvada",
            "grupo_muscular": "Costas",
            "observacoes": "N/A",
            "video": ""
        })
        assert res_edit.status_code == 403

        # Tentar excluir exercício
        res_del = client.delete("/exercicios/999", headers=headers)
        assert res_del.status_code == 403
