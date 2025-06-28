from app.extensions.db import get_db

def registrar_log_admin(acao, usuario_id=None):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO logsadmin (acao, usuario_id) VALUES (%s, %s)",
            (acao, usuario_id)
        )
    db.commit()
