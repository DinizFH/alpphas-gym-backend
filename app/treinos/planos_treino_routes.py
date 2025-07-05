from flask import Blueprint, request, jsonify
from app.extensions import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity

planos_treino_bp = Blueprint("planos_treino", __name__)

@planos_treino_bp.route("/", methods=["POST"])
@jwt_required()
def criar_plano_treino():
    dados = request.get_json()
    identidade = get_jwt_identity()

    if identidade.get("tipo_usuario") != "personal":
        return jsonify({"message": "Apenas personal pode criar planos de treino"}), 403

    id_aluno = dados.get("id_aluno")
    lista_treinos = dados.get("treinos")

    if not id_aluno or not lista_treinos or not isinstance(lista_treinos, list):
        return jsonify({"message": "Dados inválidos"}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Verificar se aluno existe
            cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario = %s AND tipo = 'aluno'", (id_aluno,))
            if not cursor.fetchone():
                return jsonify({"message": "Aluno não encontrado"}), 404

            # Criar plano
            cursor.execute("""
                INSERT INTO planos_treino (id_aluno) VALUES (%s)
            """, (id_aluno,))
            id_plano = cursor.lastrowid

            for treino in lista_treinos:
                nome_treino = treino.get("nome_treino")
                exercicios = treino.get("exercicios")

                if not nome_treino or not exercicios:
                    continue

                cursor.execute("""
                    INSERT INTO treinos (id_aluno, nome_treino, id_plano, ativo) 
                    VALUES (%s, %s, %s, TRUE)
                """, (id_aluno, nome_treino, id_plano))
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
                        ex.get("observacoes", "")
                    ))

            db.commit()
            return jsonify({"message": "Plano de treino criado com sucesso", "id_plano": id_plano}), 201
    except Exception as e:
        print("Erro ao criar plano de treino:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()
