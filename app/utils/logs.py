from app.extensions.db import get_db
from datetime import datetime

def registrar_log_envio(id_aluno, tipo_envio, destino, status, mensagem=None):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (id_aluno, tipo_envio, destino, status, mensagem, data_hora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_aluno, tipo_envio, destino, status, mensagem, datetime.now()))
        db.commit()
