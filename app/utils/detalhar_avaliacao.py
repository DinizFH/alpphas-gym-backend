from app.extensions.db import get_db

def detalhar_avaliacao_para_uso(id_avaliacao):
    db = get_db()
    with db.cursor() as cursor:
        # Buscar dados principais da avaliação e dos usuários envolvidos
        cursor.execute("""
            SELECT a.*, 
                   u.nome AS nome_aluno,
                   u.email AS email_aluno,
                   u.whatsapp AS whatsapp_aluno,
                   p.nome AS nome_profissional,
                   p.email AS email_profissional,
                   p.telefone AS telefone_profissional
            FROM avaliacoesfisicas a
            JOIN usuarios u ON a.id_aluno = u.id_usuario
            JOIN usuarios p ON a.id_profissional = p.id_usuario
            WHERE a.id_avaliacao = %s
        """, (id_avaliacao,))
        dados = cursor.fetchone()

        if not dados:
            return None

        # Montar dicionário estruturado
        avaliacao = {
            "id": dados.get("id_avaliacao"),
            "data": dados.get("data_avaliacao").strftime("%d/%m/%Y") if dados.get("data_avaliacao") else "Não informada",
            "nome_aluno": dados.get("nome_aluno", "Não informado"),
            "email_aluno": dados.get("email_aluno", ""),
            "whatsapp_aluno": dados.get("whatsapp_aluno", ""),
            "id_aluno": dados.get("id_aluno"),
            "nome_profissional": dados.get("nome_profissional", "Não informado"),
            "email": dados.get("email_profissional", ""),
            "telefone": dados.get("telefone_profissional", ""),
            "id_profissional": dados.get("id_profissional"),
            "medidas": {
                "peso": dados.get("peso", 0),
                "altura": dados.get("altura", 0),
                "imc": dados.get("imc", 0),
                "percentual_gordura": dados.get("percentual_gordura", 0),
                "massa_magra": dados.get("massa_magra", 0),
                "massa_gorda": dados.get("massa_gorda", 0),
                "braco_d_contraido": dados.get("braco_d_contraido", 0),
                "braco_e_contraido": dados.get("braco_e_contraido", 0),
                "cintura": dados.get("cintura", 0),
                "quadril": dados.get("quadril", 0),
                "peitoral": dados.get("peitoral", 0),
                "abdomen": dados.get("abdomen", 0),
                "coxa": dados.get("coxa", 0),
                "panturrilha": dados.get("panturrilha", 0),
                "dobra_triceps": dados.get("dobra_triceps", 0),
                "dobra_subescapular": dados.get("dobra_subescapular", 0),
                "dobra_biceps": dados.get("dobra_biceps", 0),
                "dobra_axilar_media": dados.get("dobra_axilar_media", 0),
                "dobra_supra_iliaca": dados.get("dobra_supra_iliaca", 0),
            },
            "observacoes": dados.get("observacoes") or ""
        }

        return avaliacao
