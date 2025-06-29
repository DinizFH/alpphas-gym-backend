from app.extensions.db import get_db

def registrar_log_envio(id_usuario, tipo, destino, status, mensagem=""):
    acao = f"Envio {tipo} - {status}"
    detalhes = f"Destino: {destino}\nMensagem: {mensagem}"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (id_usuario, acao, detalhes)
            VALUES (%s, %s, %s)
        """, (id_usuario, acao, detalhes))
        db.commit()
