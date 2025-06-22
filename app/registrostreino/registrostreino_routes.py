from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
from pymysql.err import IntegrityError
import json
from datetime import datetime
import pytz
from app.utils.jwt import extrair_user_info

registrostreino_bp = Blueprint("registrostreino", __name__)

def extrair_user_info():
    identidade_raw = get_jwt_identity()
    try:
        return json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
    except Exception:
        return {}

# ======================
# Criar novo registro de treino
# ======================
@registrostreino_bp.route("/", methods=["POST"])
@jwt_required()
def criar_registro():
    user = extrair_user_info()

    if user["tipo_usuario"] not in ["aluno", "personal"]:
        return jsonify({"message": "Apenas alunos ou personal podem registrar treinos"}), 403

    data = request.get_json()
    id_treino = data.get("id_treino")
    observacoes = data.get("observacoes", "")
    id_aluno = data.get("id_aluno") if user["tipo_usuario"] == "personal" else user["id"]

    if not id_treino:
        return jsonify({"message": "ID do treino é obrigatório"}), 400

    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    data_execucao = datetime.now(fuso_brasil).strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO registrostreino (id_aluno, id_treino, observacoes, data_execucao, ativo)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (id_aluno, id_treino, observacoes, data_execucao))
            id_registro = cursor.lastrowid

            for item in data.get("cargas", []):
                cursor.execute("""
                    INSERT INTO registrostreino_exercicios (id_registro, id_exercicio, carga)
                    VALUES (%s, %s, %s)
                """, (id_registro, item["id_exercicio"], item["carga"]))

            db.commit()
            return jsonify({"message": "Registro criado com sucesso", "id_registro": id_registro}), 201

    except IntegrityError as e:
        db.rollback()
        print("Erro de integridade ao criar registro:", e)
        return jsonify({"message": "Treino ou aluno não encontrado"}), 404

    except Exception as e:
        db.rollback()
        print("Erro ao criar registro:", e)
        return jsonify({"message": f"Erro ao criar registro: {str(e)}"}), 500

# ======================
# Listar todos os registros
# ======================
@registrostreino_bp.route("/", methods=["GET"])
@jwt_required()
def listar_registros():
    user = extrair_user_info()
    db = get_db()
    try:
        with db.cursor() as cursor:
            if user["tipo_usuario"] == "personal":
                cursor.execute("""
                    SELECT r.id_registro, r.id_treino, t.nome_treino, r.data_execucao, r.observacoes,
                           u.nome AS nome_aluno
                    FROM registrostreino r
                    JOIN treinos t ON r.id_treino = t.id_treino
                    JOIN usuarios u ON r.id_aluno = u.id_usuario
                    WHERE r.ativo = TRUE
                    ORDER BY r.data_execucao DESC
                """)
            else:
                cursor.execute("""
                    SELECT r.id_registro, r.id_treino, t.nome_treino, r.data_execucao, r.observacoes
                    FROM registrostreino r
                    JOIN treinos t ON r.id_treino = t.id_treino
                    WHERE r.id_aluno = %s AND r.ativo = TRUE
                    ORDER BY r.data_execucao DESC
                """, (user["id"],))

            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao listar registros: {str(e)}"}), 500

# ======================
# Obter registro específico
# ======================
@registrostreino_bp.route("/<int:id_registro>", methods=["GET"])
@jwt_required()
def obter_registro(id_registro):
    user = extrair_user_info()
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id_registro, r.data_execucao, r.observacoes, r.id_aluno,
                       u.nome AS nome_aluno, t.nome_treino, p.nome AS nome_profissional
                FROM registrostreino r
                JOIN usuarios u ON r.id_aluno = u.id_usuario
                JOIN treinos t ON r.id_treino = t.id_treino
                LEFT JOIN usuarios p ON t.id_profissional = p.id_usuario
                WHERE r.id_registro = %s AND r.ativo = TRUE
            """, (id_registro,))
            registro = cursor.fetchone()
            if not registro:
                return jsonify({"message": "Registro não encontrado"}), 404

            if user["tipo_usuario"] == "aluno" and user["id"] != registro["id_aluno"]:
                return jsonify({"message": "Acesso negado"}), 403

            cursor.execute("""
                SELECT e.id_exercicio, e.nome, e.grupo_muscular, re.carga
                FROM registrostreino_exercicios re
                JOIN exercicios e ON re.id_exercicio = e.id_exercicio
                WHERE re.id_registro = %s
            """, (id_registro,))
            registro["exercicios"] = cursor.fetchall()

            return jsonify(registro), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar registro: {str(e)}"}), 500

# ======================
# Atualizar registro (observações e cargas)
# ======================
@registrostreino_bp.route("/<int:id_registro>", methods=["PUT"])
@jwt_required()
def atualizar_registro(id_registro):
    user = extrair_user_info()
    data = request.get_json()
    observacoes = data.get("observacoes", "")
    cargas = data.get("cargas", [])

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_aluno FROM registrostreino
                WHERE id_registro = %s AND ativo = TRUE
            """, (id_registro,))
            registro = cursor.fetchone()
            if not registro:
                return jsonify({"message": "Registro não encontrado"}), 404
            if user["tipo_usuario"] == "aluno" and registro["id_aluno"] != user["id"]:
                return jsonify({"message": "Acesso negado"}), 403

            cursor.execute("""
                UPDATE registrostreino SET observacoes = %s WHERE id_registro = %s
            """, (observacoes, id_registro))

            cursor.execute("DELETE FROM registrostreino_exercicios WHERE id_registro = %s", (id_registro,))
            for item in cargas:
                cursor.execute("""
                    INSERT INTO registrostreino_exercicios (id_registro, id_exercicio, carga)
                    VALUES (%s, %s, %s)
                """, (id_registro, item["id_exercicio"], item["carga"]))

            db.commit()
            return jsonify({"message": "Registro atualizado com sucesso"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Erro ao atualizar registro: {str(e)}"}), 500

# ======================
# Excluir registro (aluno ou personal)
# ======================
@registrostreino_bp.route("/<int:id_registro>", methods=["DELETE"])
@jwt_required()
def excluir_registro(id_registro):
    user = extrair_user_info()
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_aluno FROM registrostreino
                WHERE id_registro = %s AND ativo = TRUE
            """, (id_registro,))
            registro = cursor.fetchone()
            if not registro:
                return jsonify({"message": "Registro não encontrado"}), 404
            if user["tipo_usuario"] == "aluno" and registro["id_aluno"] != user["id"]:
                return jsonify({"message": "Acesso negado"}), 403

            cursor.execute("""
                UPDATE registrostreino SET ativo = FALSE WHERE id_registro = %s
            """, (id_registro,))
            db.commit()
            return jsonify({"message": "Registro excluído com sucesso"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Erro ao excluir registro: {str(e)}"}), 500

# ======================
# Buscar registros por nome de aluno (personal)
# ======================
@registrostreino_bp.route("/aluno", methods=["GET"])
@jwt_required()
def buscar_registros_por_nome_aluno():
    user = extrair_user_info()
    if user.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode acessar esta rota"}), 403

    nome = request.args.get("nome", "")
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id_registro, r.data_execucao, r.observacoes,
                       u.nome AS nome_aluno, t.nome_treino
                FROM registrostreino r
                JOIN treinos t ON r.id_treino = t.id_treino
                JOIN usuarios u ON r.id_aluno = u.id_usuario
                WHERE u.nome LIKE %s AND r.ativo = TRUE
                ORDER BY r.data_execucao DESC
            """, (f"%{nome}%",))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"message": "Erro ao buscar registros"}), 500

# ======================
# Listar registros do aluno logado
# ======================
@registrostreino_bp.route("/meus", methods=["GET"])
@jwt_required()
def listar_registros_do_aluno():
    user = extrair_user_info()
    if user.get("tipo_usuario") != "aluno":
        return jsonify({"message": "Apenas alunos podem acessar esta rota"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.id_registro, r.id_treino, t.nome_treino, r.data_execucao, r.observacoes
                FROM registrostreino r
                JOIN treinos t ON r.id_treino = t.id_treino
                WHERE r.id_aluno = %s AND r.ativo = TRUE
                ORDER BY r.data_execucao DESC
            """, (user["id"],))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao buscar seus registros: {str(e)}"}), 500

# ======================
# Buscar última carga por exercício
# ======================
@registrostreino_bp.route("/ultima-carga/<int:id_exercicio>", methods=["GET"])
@jwt_required()
def ultima_carga_exercicio(id_exercicio):
    identidade = extrair_user_info()
    id_aluno = identidade.get("id")
    tipo_usuario = identidade.get("tipo_usuario")

    if tipo_usuario == "personal":
        # Personal pode passar o ID do aluno via query string
        id_aluno_param = request.args.get("id_aluno", type=int)
        if id_aluno_param:
            id_aluno = id_aluno_param

    if not id_aluno:
        return jsonify({"message": "ID do aluno não fornecido"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT rtex.carga
                FROM registrostreino rt
                JOIN registrostreino_exercicios rtex ON rt.id_registro = rtex.id_registro
                WHERE rt.ativo = TRUE
                  AND rtex.id_exercicio = %s
                  AND rt.id_aluno = %s
                ORDER BY rt.data_execucao DESC, rt.id_registro DESC
                LIMIT 1
            """, (id_exercicio, id_aluno))
            result = cursor.fetchone()

            if result:
                return jsonify({"ultima_carga": float(result["carga"])})
            else:
                return jsonify({"ultima_carga": None})
    except Exception as e:
        print("Erro ao buscar última carga:", e)
        return jsonify({"message": "Erro ao buscar última carga"}), 500