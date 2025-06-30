# app/utils/logs.py

from datetime import datetime
from app.extensions.db import get_db

def registrar_log_envio(id_usuario, tipo_envio, destino, conteudo, status):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (id_usuario, tipo_log, tipo_envio, destino, conteudo, status, data_envio)
            VALUES (%s, 'envio', %s, %s, %s, %s, %s)
        """, (id_usuario, tipo_envio, destino, conteudo, status, datetime.now()))
        db.commit()

def registrar_log_acao(usuario_origem, acao, detalhes=""):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (tipo_log, usuario_origem, acao, detalhes, data)
            VALUES ('acao', %s, %s, %s, %s)
        """, (usuario_origem, acao, detalhes, datetime.now()))
        db.commit()
