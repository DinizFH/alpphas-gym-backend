from datetime import datetime
from app.extensions.db import get_db

def registrar_log_envio(id_aluno, tipo_envio, destino, status, mensagem=None):
    """
    Registra um log de envio de plano alimentar.

    Parâmetros:
    - id_aluno: ID do aluno destinatário
    - tipo_envio: "email" ou "whatsapp"
    - destino: e-mail ou número de telefone
    - status: "sucesso" ou "erro"
    - mensagem: (opcional) descrição adicional do status
    """
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (id_aluno, tipo_envio, destino, status, mensagem, data_hora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_aluno,
            tipo_envio,
            destino,
            status,
            mensagem,
            datetime.now()
        ))
        db.commit()
