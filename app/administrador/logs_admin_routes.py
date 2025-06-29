from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.utils.jwt import extrair_user_info
from app.extensions.db import get_db

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
    tipo = request.args.get("tipo")
    id_usuario = request.args.get("id_usuario")
    data_inicio = request.args.get("data_inicio")  # formato: YYYY-MM-DD
    data_fim = request.args.get("data_fim")        # formato: YYYY-MM-DD
    offset = int(request.args.get("offset", 0))

    filtros = []
    valores = []

    if tipo:
        filtros.append("l.tipo_envio = %s")
        valores.append(tipo)

    if id_usuario:
        filtros.append("l.id_aluno = %s")
        valores.append(id_usuario)

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

    return jsonify(logs), 200

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
