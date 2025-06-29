from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.utils.jwt import extrair_user_info
from app.extensions.db import get_db
from datetime import datetime

logs_admin_bp = Blueprint("logs_admin", __name__)

# =========================
# Listar logs com filtros e paginação
# =========================
@logs_admin_bp.route("/admin/logs", methods=["GET"])
@jwt_required()
def listar_logs():
    identidade = extrair_user_info()
    if identidade.get("email") != "administrador@alpphasgym.com":
        return jsonify({"message": "Acesso não autorizado"}), 403

    # Filtros opcionais
    tipo_envio = request.args.get("tipo_envio")
    id_usuario = request.args.get("id_usuario")
    status = request.args.get("status")
    data_inicio = request.args.get("data_inicio")  # formato: YYYY-MM-DD
    data_fim = request.args.get("data_fim")        # formato: YYYY-MM-DD
    offset = int(request.args.get("offset", 0))

    filtros = []
    valores = []

    if tipo_envio:
        filtros.append("l.tipo_envio = %s")
        valores.append(tipo_envio)

    if id_usuario:
        filtros.append("l.id_aluno = %s")
        valores.append(id_usuario)

    if status:
        filtros.append("l.status = %s")
        valores.append(status)

    if data_inicio:
        filtros.append("DATE(l.data_hora) >= %s")
        valores.append(data_inicio)

    if data_fim:
        filtros.append("DATE(l.data_hora) <= %s")
        valores.append(data_fim)

    where_sql = "WHERE " + " AND ".join(filtros) if filtros else ""

    query = f"""
        SELECT l.id_log, l.tipo_envio, l.destino, l.status, l.mensagem, l.data_hora,
               u.nome AS nome_usuario, u.email
        FROM logs l
        LEFT JOIN usuarios u ON l.id_aluno = u.id_usuario
        {where_sql}
        ORDER BY l.data_hora DESC
        LIMIT 10 OFFSET %s
    """
    valores.append(offset)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, valores)
        logs = cursor.fetchall()

    return jsonify(logs)

# =========================
# Limpar todos os logs
# =========================
@logs_admin_bp.route("/admin/logs", methods=["DELETE"])
@jwt_required()
def limpar_logs():
    identidade = extrair_user_info()
    if identidade.get("email") != "administrador@alpphasgym.com":
        return jsonify({"message": "Acesso não autorizado"}), 403

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM logs")
        db.commit()

    return jsonify({"message": "Todos os logs foram apagados com sucesso."}), 200

# =========================
# Obter detalhes de um log específico
# =========================
@logs_admin_bp.route("/admin/logs/<int:id_log>", methods=["GET"])
@jwt_required()
def obter_log(id_log):
    identidade = extrair_user_info()
    if identidade.get("email") != "administrador@alpphasgym.com":
        return jsonify({"message": "Acesso não autorizado"}), 403

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT l.*, u.nome AS nome_usuario, u.email
            FROM logs l
            LEFT JOIN usuarios u ON l.id_aluno = u.id_usuario
            WHERE l.id_log = %s
        """, (id_log,))
        log = cursor.fetchone()

    if not log:
        return jsonify({"message": "Log não encontrado."}), 404

    return jsonify(log), 200

# =========================
# Exportar logs em CSV (formato JSON para frontend converter)
# =========================
@logs_admin_bp.route("/admin/logs/exportar", methods=["GET"])
@jwt_required()
def exportar_logs():
    identidade = extrair_user_info()
    if identidade.get("email") != "administrador@alpphasgym.com":
        return jsonify({"message": "Acesso não autorizado"}), 403

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT l.id_log, l.tipo_envio, l.destino, l.status, l.mensagem, l.data_hora,
                   u.nome AS nome_usuario, u.email
            FROM logs l
            LEFT JOIN usuarios u ON l.id_aluno = u.id_usuario
            ORDER BY l.data_hora DESC
        """)
        registros = cursor.fetchall()

    return jsonify(registros), 200
