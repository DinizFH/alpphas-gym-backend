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
            "id": dados["id_avaliacao"],
            "data": dados["data_avaliacao"].strftime("%d/%m/%Y") if dados["data_avaliacao"] else "Não informada",
            "nome_aluno": dados["nome_aluno"],
            "email_aluno": dados["email_aluno"],
            "whatsapp_aluno": dados["whatsapp_aluno"],
            "id_aluno": dados["id_aluno"],
            "nome_profissional": dados["nome_profissional"],
            "email": dados["email_profissional"],
            "telefone": dados["telefone_profissional"],
            "id_profissional": dados["id_profissional"],
            "medidas": {
                "peso": dados["peso"],
                "altura": dados["altura"],
                "imc": dados["imc"],
                "percentual_gordura": dados["percentual_gordura"],
                "massa_magra": dados["massa_magra"],
                "massa_gorda": dados["massa_gorda"],
                "braco_d_contraido": dados["braco_d_contraido"],
                "braco_e_contraido": dados["braco_e_contraido"],
                "cintura": dados["cintura"],
                "quadril": dados["quadril"],
                "peitoral": dados["peitoral"],
                "abdomen": dados["abdomen"],
                "coxa": dados["coxa"],
                "panturrilha": dados["panturrilha"],
                "dobra_triceps": dados["dobra_triceps"],
                "dobra_subescapular": dados["dobra_subescapular"],
                "dobra_biceps": dados["dobra_biceps"],
                "dobra_axilar_media": dados["dobra_axilar_media"],
                "dobra_supra_iliaca": dados["dobra_supra_iliaca"],
            },
            "observacoes": dados.get("observacoes") or ""
        }

        return avaliacao
