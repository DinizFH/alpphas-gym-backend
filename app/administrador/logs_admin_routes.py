from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.utils.jwt import extrair_user_info
from app.extensions.db import get_db

logs_admin_bp = Blueprint("logs_admin", __name__)

@logs_admin_bp.route("/admin/logs", methods=["GET"])
@jwt_required()
def listar_logs():
    identidade = extrair_user_info()
    if identidade.get("email") != "administrador@alpphasgym.com":
        return jsonify({"message": "Acesso não autorizado"}), 403

    # Filtros opcionais da query string
    tipo = request.args.get("tipo")
    id_usuario = request.args.get("id_usuario")
    data_inicio = request.args.get("data_inicio")  # formato: YYYY-MM-DD
    data_fim = request.args.get("data_fim")        # formato: YYYY-MM-DD

    filtros = []
    valores = []

    if tipo:
        filtros.append("l.tipo_acao = %s")
        valores.append(tipo)

    if id_usuario:
        filtros.append("l.id_usuario = %s")
        valores.append(id_usuario)

    if data_inicio:
        filtros.append("DATE(l.data_hora) >= %s")
        valores.append(data_inicio)

    if data_fim:
        filtros.append("DATE(l.data_hora) <= %s")
        valores.append(data_fim)

    where_sql = "WHERE " + " AND ".join(filtros) if filtros else ""

    query = f"""
        SELECT l.id_log, l.tipo_acao, l.descricao, l.data_hora,
               u.nome AS nome_usuario, u.email
        FROM logs l
        LEFT JOIN usuarios u ON l.id_usuario = u.id_usuario
        {where_sql}
        ORDER BY l.data_hora DESC
        LIMIT 100
    """

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, valores)
        logs = cursor.fetchall()

    return jsonify(logs)
