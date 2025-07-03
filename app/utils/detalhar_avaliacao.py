from app.extensions.db import get_db
from datetime import datetime

def detalhar_avaliacao_para_uso(id_avaliacao):
    db = get_db()
    with db.cursor() as cursor:
        # Buscar dados da avaliação
        cursor.execute("""
            SELECT a.*, u.nome AS nome_aluno, p.nome AS nome_profissional, p.email, p.telefone, p.cref, p.crn
            FROM avaliacoesfisicas a
            JOIN usuarios u ON a.id_aluno = u.id_usuario
            JOIN usuarios p ON a.id_profissional = p.id_usuario
            WHERE a.id_avaliacao = %s
        """, (id_avaliacao,))
        avaliacao = cursor.fetchone()

    if not avaliacao:
        return None

    # Formatando data da avaliação
    if avaliacao.get("data_avaliacao"):
        try:
            data_obj = avaliacao["data_avaliacao"]
            if isinstance(data_obj, str):
                data_obj = datetime.strptime(data_obj, "%Y-%m-%d")
            avaliacao["data_avaliacao_formatada"] = data_obj.strftime("%d/%m/%Y")
        except Exception:
            avaliacao["data_avaliacao_formatada"] = "Data inválida"

    return avaliacao
