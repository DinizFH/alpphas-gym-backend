# app/utils/logs.py

from datetime import datetime
from app.extensions.db import get_db

def registrar_log_envio(id_usuario, tipo_envio, destino, conteudo, status):
    """
    Registra um log de envio no banco de dados.
    
    Parâmetros:
    - id_usuario: int — ID do usuário que recebeu ou enviou
    - tipo_envio: str — 'email' ou 'whatsapp'
    - destino: str — endereço de e-mail ou número de telefone
    - conteudo: str — descrição do conteúdo enviado
    - status: str — 'sucesso', 'falha', etc
    """
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (id_usuario, tipo_envio, destino, conteudo, status, data_envio)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_usuario, tipo_envio, destino, conteudo, status, datetime.now()))
        db.commit()
