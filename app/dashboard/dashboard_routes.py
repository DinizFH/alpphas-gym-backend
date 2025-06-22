from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
import json

dashboard_bp = Blueprint("dashboard", __name__)


def extrair_user_info():
    identidade = get_jwt_identity()
    try:
        return json.loads(identidade) if isinstance(identidade, str) else identidade
    except Exception as e:
        print(f"[ERRO] Falha ao decodificar identidade JWT: {e}")
        return None


@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def dashboard():
    identidade = extrair_user_info()
    if not identidade:
        return jsonify({'message': 'Identidade inválida'}), 401

    user_id = identidade.get("id")
    user_tipo = identidade.get("tipo_usuario")

    db = get_db()
    if db is None:
        return jsonify({'message': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with db.cursor() as cursor:
            # Perfil do usuário
            cursor.execute("""
                SELECT id_usuario, nome, email, tipo_usuario
                FROM usuarios
                WHERE id_usuario = %s AND ativo = TRUE
            """, (user_id,))
            perfil = cursor.fetchone()

            if not perfil:
                return jsonify({'message': 'Usuário não encontrado'}), 404

            dashboard_data = {
                "perfil": {
                    "id_usuario": perfil["id_usuario"],
                    "nome": perfil["nome"],
                    "email": perfil["email"],
                    "tipo_usuario": perfil["tipo_usuario"]
                }
            }

            # ========================
            # DASHBOARD DO ALUNO
            # ========================
            if user_tipo == "aluno":
                # Agendamentos futuros
                cursor.execute("""
                    SELECT id_agendamento, tipo_agendamento, data_hora_inicio
                    FROM agendamentos
                    WHERE id_aluno = %s AND status = 'marcado' AND data_hora_inicio >= NOW()
                    ORDER BY data_hora_inicio ASC
                    LIMIT 5
                """, (user_id,))
                dashboard_data["proximos_agendamentos"] = cursor.fetchall()

                # Avaliações recentes
                cursor.execute("""
                    SELECT data_avaliacao, peso, percentual_gordura, imc
                    FROM avaliacoesfisicas
                    WHERE id_aluno = %s
                    ORDER BY data_avaliacao DESC
                    LIMIT 3
                """, (user_id,))
                dashboard_data["avaliacoes_recentes"] = cursor.fetchall()

                # Execuções de treino recentes
                cursor.execute("""
                    SELECT t.nome_treino, r.data_execucao, r.observacoes
                    FROM registrostreino r
                    JOIN treinos t ON r.id_treino = t.id_treino
                    WHERE r.id_aluno = %s
                    ORDER BY r.data_execucao DESC
                    LIMIT 5
                """, (user_id,))
                dashboard_data["execucoes_recentes"] = cursor.fetchall()

                # Plano alimentar atual
                cursor.execute("""
                    SELECT id_plano, titulo, descricao_geral
                    FROM planosalimentares
                    WHERE id_aluno = %s AND ativo = TRUE
                    ORDER BY id_plano DESC
                    LIMIT 1
                """, (user_id,))
                plano = cursor.fetchone()
                dashboard_data["plano_alimentar"] = plano if plano else {}

                # Todos os treinos
                cursor.execute("""
                    SELECT id_treino, nome_treino, objetivo
                    FROM treinos
                    WHERE id_aluno = %s AND ativo = TRUE
                    ORDER BY id_treino DESC
                """, (user_id,))
                dashboard_data["treinos"] = cursor.fetchall()

                # Todas as avaliações
                cursor.execute("""
                    SELECT id_avaliacao, data_avaliacao, peso, altura, imc, percentual_gordura
                    FROM avaliacoesfisicas
                    WHERE id_aluno = %s
                    ORDER BY data_avaliacao DESC
                """, (user_id,))
                dashboard_data["avaliacoes"] = cursor.fetchall()

                # Todos os planos alimentares
                cursor.execute("""
                    SELECT id_plano, titulo, descricao_geral, ativo
                    FROM planosalimentares
                    WHERE id_aluno = %s
                    ORDER BY id_plano DESC
                """, (user_id,))
                dashboard_data["planos"] = cursor.fetchall()

            # ========================
            # DASHBOARD DO PERSONAL / NUTRICIONISTA
            # ========================
            elif user_tipo in ["personal", "nutricionista"]:
                # Atendimentos futuros
                cursor.execute("""
                    SELECT a.id_agendamento, a.tipo_agendamento, a.data_hora_inicio, u.nome AS aluno
                    FROM agendamentos a
                    JOIN usuarios u ON a.id_aluno = u.id_usuario
                    WHERE a.id_profissional = %s AND a.status = 'marcado' AND a.data_hora_inicio >= NOW()
                    ORDER BY a.data_hora_inicio ASC
                    LIMIT 5
                """, (user_id,))
                dashboard_data["proximos_atendimentos"] = cursor.fetchall()

                # Total de alunos vinculados
                cursor.execute("""
                    SELECT COUNT(DISTINCT id_aluno) AS total
                    FROM agendamentos
                    WHERE id_profissional = %s
                """, (user_id,))
                resultado = cursor.fetchone()
                dashboard_data["alunos_vinculados"] = resultado["total"] if resultado else 0

            return jsonify(dashboard_data), 200

    except Exception as e:
        print("Erro no dashboard:", e)
        return jsonify({"message": "Erro interno"}), 500
    finally:
        db.close()
