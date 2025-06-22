from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
from app.utils.jwt import extrair_user_info
import json

treinos_bp = Blueprint("treinos", __name__)

def extrair_user_info():
    identidade = get_jwt_identity()
    try:
        return json.loads(identidade) if isinstance(identidade, str) else identidade
    except Exception:
        return {}

# =======================
# Criar novo treino
# =======================
@treinos_bp.route("/", methods=["POST"])
@jwt_required()
def criar_treino():
    identidade = extrair_user_info()
    print("DEBUG - Identidade recebida no treino:", identidade)
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Treino criado com sucesso", "id": id_treino}), 201

    data = request.get_json()
    id_aluno = data.get("id_aluno")
    nome_treino = data.get("nome_treino")
    exercicios = data.get("exercicios", [])

    if not all([id_aluno, nome_treino]) or not exercicios:
        return jsonify({"message": "Campos obrigatórios não fornecidos"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO treinos (id_aluno, id_profissional, nome_treino, ativo)
                VALUES (%s, %s, %s, TRUE)
            """, (id_aluno, identidade.get("id"), nome_treino))
            id_treino = cursor.lastrowid

            for ex in exercicios:
                cursor.execute("""
                    INSERT INTO treinoexercicios (id_treino, id_exercicio, series, repeticoes, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_treino,
                    ex.get("id_exercicio"),
                    ex.get("series"),
                    ex.get("repeticoes"),
                    ex.get("observacoes")
                ))

            db.commit()
            return jsonify({
                "message": "Treino criado com sucesso",
                "id_treino": id_treino   # ✅ corrigido
            }), 201

    except Exception as e:
        print("Erro ao criar treino:", e)
        return jsonify({"message": "Erro interno"}), 500

    finally:
        db.close()


# =======================
# Listar treinos por profissional
# =======================
@treinos_bp.route("/profissional", methods=["GET"])
@jwt_required()
def listar_treinos_por_profissional():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode acessar"}), 403

    nome = request.args.get("nome", "")

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT u.id_usuario, u.nome, u.cpf, t.id_treino, t.nome_treino
                FROM usuarios u
                JOIN treinos t ON u.id_usuario = t.id_aluno
                WHERE t.id_profissional = %s AND t.ativo = TRUE AND u.nome LIKE %s
                ORDER BY u.nome, t.nome_treino
            """, (identidade.get("id"), f"%{nome}%"))
            dados = cursor.fetchall()

            resposta = {}
            for row in dados:
                uid = row["id_usuario"]
                if uid not in resposta:
                    resposta[uid] = {
                        "id_usuario": uid,
                        "nome": row["nome"],
                        "cpf": row["cpf"],
                        "treinos": []
                    }
                resposta[uid]["treinos"].append({
                    "id_treino": row["id_treino"],
                    "nome_treino": row["nome_treino"]
                })
            return jsonify(list(resposta.values())), 200
    except Exception as e:
        print("Erro ao listar treinos:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Obter detalhes do treino
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["GET"])
@jwt_required()
def detalhes_treino(id_treino):
    identidade = extrair_user_info()
    tipo = identidade.get("tipo_usuario")
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT t.id_treino, t.nome_treino, t.id_aluno, u.nome AS nome_aluno, u.cpf AS cpf_aluno
                FROM treinos t
                JOIN usuarios u ON u.id_usuario = t.id_aluno
                WHERE t.id_treino = %s AND t.ativo = TRUE
            """, (id_treino,))
            treino = cursor.fetchone()
            if not treino:
                return jsonify({"message": "Treino não encontrado"}), 404

            # Proteção: aluno só acessa seus próprios treinos
            if tipo == "aluno" and treino["id_aluno"] != identidade.get("id"):
                return jsonify({"message": "Acesso negado"}), 403

            # Corrigido: nomes dos campos como 'nome' e 'grupo_muscular'
            cursor.execute("""
                SELECT e.id_exercicio, e.nome, e.grupo_muscular, te.series, te.repeticoes, te.observacoes
                FROM treinoexercicios te
                JOIN exercicios e ON te.id_exercicio = e.id_exercicio
                WHERE te.id_treino = %s
            """, (id_treino,))
            treino["exercicios"] = cursor.fetchall()

            return jsonify(treino), 200
    except Exception as e:
        print("Erro ao obter treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()



# =======================
# Editar treino
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["PUT"])
@jwt_required()
def editar_treino(id_treino):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode editar treinos"}), 403

    data = request.get_json()
    nome_treino = data.get("nome_treino")
    exercicios = data.get("exercicios", [])

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE treinos SET nome_treino = %s WHERE id_treino = %s
            """, (nome_treino, id_treino))

            cursor.execute("DELETE FROM treinoexercicios WHERE id_treino = %s", (id_treino,))
            for ex in exercicios:
                cursor.execute("""
                    INSERT INTO treinoexercicios (id_treino, id_exercicio, series, repeticoes, observacoes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_treino, ex["id_exercicio"], ex["series"], ex["repeticoes"], ex["observacoes"]))

            db.commit()
            return jsonify({"message": "Treino atualizado com sucesso"}), 200
    except Exception as e:
        print("Erro ao editar treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Excluir treino (inativar)
# =======================
@treinos_bp.route("/<int:id_treino>", methods=["DELETE"])
@jwt_required()
def excluir_treino(id_treino):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode excluir treinos"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE treinos SET ativo = FALSE WHERE id_treino = %s", (id_treino,))
            db.commit()
            return jsonify({"message": "Treino excluído com sucesso"}), 200
    except Exception as e:
        print("Erro ao excluir treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Listar treinos do aluno logado
# =======================
@treinos_bp.route("/aluno", methods=["GET"])
@jwt_required()
def listar_treinos_aluno():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "aluno":
        return jsonify({"message": "Apenas alunos podem acessar esta rota"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_treino, nome_treino
                FROM treinos
                WHERE id_aluno = %s AND ativo = TRUE
                ORDER BY nome_treino
            """, (identidade.get("id"),))
            treinos = cursor.fetchall()
            return jsonify(treinos), 200
    except Exception as e:
        print("Erro ao listar treinos do aluno:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()


# =======================
# Listar treinos de um aluno por ID (usado por personal)
# =======================
@treinos_bp.route("/aluno/<int:id_aluno>", methods=["GET"])
@jwt_required()
def listar_treinos_de_um_aluno(id_aluno):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode acessar esta rota"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_treino, nome_treino
                FROM treinos
                WHERE id_aluno = %s AND ativo = TRUE
                ORDER BY nome_treino
            """, (id_aluno,))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar treinos do aluno:", e)
        return jsonify({"message": "Erro interno ao listar treinos"}), 500
    finally:
        db.close()