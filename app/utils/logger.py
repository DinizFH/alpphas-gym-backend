# utils/logger.py
from app.extensions.db import get_db
from datetime import datetime

def registrar_log(email, acao, detalhes=""):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs (usuario_email, acao, detalhes, data_hora)
                VALUES (%s, %s, %s, %s)
            """, (email, acao, detalhes, datetime.now()))
        db.commit()
    except Exception as e:
        print("Erro ao registrar log:", e)
