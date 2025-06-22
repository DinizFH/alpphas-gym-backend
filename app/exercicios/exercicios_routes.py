from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions.db import get_db
from app.utils.jwt import extrair_user_info

exercicios_bp = Blueprint("exercicios", __name__)

# =======================
# Criar exercício (somente personal)
# =======================
@exercicios_bp.route("/", methods=["POST"])
@jwt_required()
def criar_exercicio():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode criar exercícios"}), 403

    data = request.get_json()
    nome = data.get("nome")
    grupo = data.get("grupo_muscular")
    observacoes = data.get("observacoes")
    video = data.get("video")

    if not nome or not grupo:
        return jsonify({"message": "Campos obrigatórios não fornecidos"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO exercicios (nome, grupo_muscular, observacoes, video)
                VALUES (%s, %s, %s, %s)
            """, (nome, grupo, observacoes, video))
            id_exercicio = cursor.lastrowid
            db.commit()
            return jsonify({
                "message": "Exercício criado com sucesso",
                "id_exercicio":id_exercicio
            }), 201
    except Exception as e:
        print("Erro ao criar exercício:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Listar exercícios (personal e aluno)
# =======================
@exercicios_bp.route("/", methods=["GET"])
@jwt_required()
def listar_exercicios():
    identidade = extrair_user_info()
    tipo = identidade.get("tipo_usuario")
    user_id = identidade.get("id")
    termo = request.args.get("nome", "")

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "aluno":
                cursor.execute("""
                    SELECT DISTINCT e.*
                    FROM exercicios e
                    JOIN treinoexercicios te ON te.id_exercicio = e.id_exercicio
                    JOIN treinos t ON t.id_treino = te.id_treino
                    WHERE t.id_aluno = %s AND t.ativo = TRUE AND e.nome LIKE %s
                """, (user_id, f"%{termo}%"))
            else:
                cursor.execute("""
                    SELECT * FROM exercicios
                    WHERE nome LIKE %s
                """, (f"%{termo}%",))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar exercícios:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Obter exercício por ID
# =======================
@exercicios_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def obter_exercicio(id):
    identidade = extrair_user_info()
    tipo = identidade.get("tipo_usuario")
    user_id = identidade.get("id")

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "aluno":
                cursor.execute("""
                    SELECT e.*
                    FROM exercicios e
                    JOIN treinoexercicios te ON te.id_exercicio = e.id_exercicio
                    JOIN treinos t ON t.id_treino = te.id_treino
                    WHERE e.id_exercicio = %s AND t.id_aluno = %s AND t.ativo = TRUE
                """, (id, user_id))
            else:
                cursor.execute("SELECT * FROM exercicios WHERE id_exercicio = %s", (id,))

            exercicio = cursor.fetchone()
            if not exercicio:
                return jsonify({"message": "Exercício não encontrado ou acesso negado"}), 404
            return jsonify(exercicio), 200
    except Exception as e:
        print("Erro ao obter exercício:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Editar exercício (somente personal)
# =======================
@exercicios_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def editar_exercicio(id):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode editar exercícios"}), 403

    data = request.get_json()
    nome = data.get("nome")
    grupo = data.get("grupo_muscular")
    observacoes = data.get("observacoes")
    video = data.get("video")

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE exercicios
                SET nome = %s, grupo_muscular = %s, observacoes = %s, video = %s
                WHERE id_exercicio = %s
            """, (nome, grupo, observacoes, video, id))
            db.commit()
            return jsonify({"message": "Exercício atualizado"}), 200
    except Exception as e:
        print("Erro ao editar exercício:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Excluir exercício (somente personal)
# =======================
@exercicios_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def excluir_exercicio(id):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode excluir exercícios"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM exercicios WHERE id_exercicio = %s", (id,))
            db.commit()
            return jsonify({"message": "Exercício excluído"}), 200
    except Exception as e:
        print("Erro ao excluir exercício:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()
