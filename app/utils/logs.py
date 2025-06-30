from datetime import datetime
from flask_jwt_extended import get_jwt_identity
import json
from app.extensions.db import get_db

def registrar_log_envio(id_usuario, tipo_envio, destino, mensagem, status):
    """
    Registra um log de envio externo (e-mail, WhatsApp).

    Parâmetros:
    - id_usuario: destinatário
    - tipo_envio: 'email' ou 'whatsapp'
    - destino: endereço de envio (e-mail ou telefone)
    - mensagem: texto da mensagem enviada
    - status: 'sucesso', 'falha: ...'
    """
    try:
        identidade_raw = get_jwt_identity()
        identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade
    except:
        identidade = {}

    conteudo = {
        "mensagem": mensagem,
        "id_enviante": identidade.get("id"),
        "nome_enviante": identidade.get("nome")
    }

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (tipo_log, id_usuario, tipo_envio, destino, conteudo, status, data_envio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            "envio",
            id_usuario,
            tipo_envio,
            destino,
            json.dumps(conteudo),
            status,
            datetime.now()
        ))
        db.commit()

def registrar_log_acao(acao, detalhes=""):
    """
    Registra uma ação interna feita por um usuário autenticado.

    Parâmetros:
    - acao: nome da ação (ex: criar_avaliacao, editar_treino, login_sucesso)
    - detalhes: string ou dicionário com mais informações (ex: id do alvo, nome, etc)
    """
    try:
        identidade_raw = get_jwt_identity()
        identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade
        email_usuario = identidade.get("email", "desconhecido")
    except:
        email_usuario = "desconhecido"

    if isinstance(detalhes, dict):
        detalhes = json.dumps(detalhes, ensure_ascii=False)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO logs (tipo_log, usuario_origem, acao, detalhes)
            VALUES (%s, %s, %s, %s)
        """, (
            "acao",
            email_usuario,
            acao,
            detalhes
        ))
        db.commit()