import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

def registrar_usuario(nome, email, senha, tipo, extra=None):
    payload = {
        "nome": nome,
        "email": email,
        "senha": senha,
        "tipo_usuario": tipo
    }
    if tipo == "personal":
        payload["cref"] = extra or "CREF999"
    elif tipo == "nutricionista":
        payload["crn"] = extra or "CRN888"

    return requests.post(f"{BASE_URL}/auth/register", json=payload)

def login(email, senha):
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "senha": senha})
    return res.json().get("access_token")

def buscar_aluno(token, nome):
    res = requests.get(f"{BASE_URL}/avaliacoes/buscar-aluno?nome={nome}", headers={"Authorization": f"Bearer {token}"})
    return res.json()[0]["id_usuario"]

def criar_exercicio(token):
    return requests.post(f"{BASE_URL}/exercicios/", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Agachamento",
        "grupo_muscular": "Pernas",
        "observacoes": "Manter postura reta",
        "video": "https://youtu.be/agachamento"
    })

def criar_treino(token, id_aluno):
    res = requests.post(f"{BASE_URL}/treinos/", headers={"Authorization": f"Bearer {token}"}, json={
        "id_aluno": id_aluno,
        "nome_treino": "Treino Popular",
        "objetivo": "Ganho de massa"
    })
    return res.json().get("id_treino")

def adicionar_exercicio_treino(token, id_treino, id_exercicio):
    return requests.post(f"{BASE_URL}/treinos/{id_treino}/exercicios", headers={"Authorization": f"Bearer {token}"}, json={
        "id_exercicio": id_exercicio,
        "series": 4,
        "repeticoes": 10,
        "observacoes": "Pegar pesado"
    })

def criar_avaliacao(token, id_aluno):
    payload = {
        "id_aluno": id_aluno,
        "idade": 30,
        "peso": 75,
        "altura": 1.78,
        "dobra_peitoral": 10,
        "dobra_triceps": 12,
        "dobra_subescapular": 8,
        "dobra_biceps": 7,
        "dobra_axilar_media": 6,
        "dobra_supra_iliaca": 9,
        "pescoco": 38, "ombro": 110, "torax": 100, "cintura": 85,
        "abdomen": 88, "quadril": 95, "braco_direito": 34, "braco_esquerdo": 33,
        "braco_d_contraido": 36, "braco_e_contraido": 35,
        "antebraco_direito": 29, "antebraco_esquerdo": 28, "coxa_direita": 57,
        "coxa_esquerda": 56, "panturrilha_direita": 40, "panturrilha_esquerda": 39,
        "observacoes": "Avaliação popular"
    }
    return requests.post(f"{BASE_URL}/avaliacoes/", headers={"Authorization": f"Bearer {token}"}, json=payload)

def criar_plano(token, id_aluno):
    res = requests.post(f"{BASE_URL}/planos/", headers={"Authorization": f"Bearer {token}"}, json={
        "id_aluno": id_aluno,
        "titulo": "Plano Popular",
        "descricao_geral": "Plano completo para testes"
    })
    id_plano = res.json().get("id_plano")
    requests.post(f"{BASE_URL}/planos/{id_plano}/refeicoes", headers={"Authorization": f"Bearer {token}"}, json={
        "horario": "08:00",
        "descricao": "Café da manhã",
        "calorias_estimadas": 500,
        "alimentos": [
            {"nome": "Pão integral", "quantidade": 2},
            {"nome": "Ovo cozido", "quantidade": 2}
        ]
    })
    requests.post(f"{BASE_URL}/planos/{id_plano}/refeicoes", headers={"Authorization": f"Bearer {token}"}, json={
        "horario": "12:00",
        "descricao": "Almoço",
        "calorias_estimadas": 700,
        "alimentos": [
            {"nome": "Arroz", "quantidade": 3},
            {"nome": "Frango grelhado", "quantidade": 1}
        ]
    })

def criar_agendamento(token, id_aluno):
    inicio = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    fim = (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S")

    return requests.post(f"{BASE_URL}/agendamentos/", headers={"Authorization": f"Bearer {token}"}, json={
        "id_aluno": id_aluno,
        "tipo_agendamento": "treino",
        "data_hora_inicio": inicio,
        "data_hora_fim": fim,
        "observacoes": "Sessão automatizada"
    })

def registrar_execucao_treino(token, id_treino):
    return requests.post(f"{BASE_URL}/registrostreino/", headers={"Authorization": f"Bearer {token}"}, json={
        "id_treino": id_treino,
        "observacoes": "Execução de teste"
    })

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    print("[*] Registrando usuários...")
    registrar_usuario("Personal Popular", "personal@popular.com", "123456", "personal", "CREF123")
    registrar_usuario("Nutri Popular", "nutri@popular.com", "123456", "nutricionista", "CRN321")
    registrar_usuario("Aluno Popular", "aluno@popular.com", "123456", "aluno")

    print("[*] Logando usuários...")
    token_personal = login("personal@popular.com", "123456")
    token_nutri = login("nutri@popular.com", "123456")
    token_aluno = login("aluno@popular.com", "123456")

    print("[*] Buscando aluno...")
    id_aluno = buscar_aluno(token_personal, "Aluno")

    print("[*] Criando exercício...")
    criar_exercicio(token_personal)
    res_exerc = requests.get(f"{BASE_URL}/exercicios/", headers={"Authorization": f"Bearer {token_personal}"})
    id_exercicio = res_exerc.json()[0]["id_exercicio"]

    print("[*] Criando treino...")
    id_treino = criar_treino(token_personal, id_aluno)
    adicionar_exercicio_treino(token_personal, id_treino, id_exercicio)

    print("[*] Criando avaliação...")
    criar_avaliacao(token_personal, id_aluno)

    print("[*] Criando plano alimentar...")
    criar_plano(token_nutri, id_aluno)

    print("[*] Criando agendamento...")
    criar_agendamento(token_personal, id_aluno)

    print("[*] Registrando execução de treino...")
    registrar_execucao_treino(token_aluno, id_treino)

    print("[✅] Banco de dados populado com sucesso!")
