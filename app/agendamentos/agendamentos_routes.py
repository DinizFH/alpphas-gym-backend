from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
import json

agendamentos_bp = Blueprint('agendamentos', __name__)


def extrair_user_info():
    try:
        identidade_raw = get_jwt_identity()
        identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
        return identidade
    except Exception as e:
        print("[ERRO] Não foi possível extrair identidade do token:", e)
        return {}

# ================================
# Criar agendamento (somente Personal ou Nutricionista)
# ================================
@agendamentos_bp.route('/', methods=['POST'])
@jwt_required()
def criar_agendamento():
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({'msg': 'Apenas personal ou nutricionista podem criar agendamentos'}), 403

    data = request.get_json()
    id_aluno = data.get('id_aluno')
    id_profissional = identidade.get("id")
    tipo = data.get('tipo_agendamento')
    inicio = data.get('data_hora_inicio')
    fim = data.get('data_hora_fim')
    observacoes = data.get('observacoes')

    if not all([id_aluno, id_profissional, tipo, inicio]):
        return jsonify({'msg': 'Campos obrigatórios não fornecidos'}), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO agendamentos (
                    id_aluno, id_profissional, tipo_agendamento,
                    data_hora_inicio, data_hora_fim, observacoes, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'marcado')
            """, (id_aluno, id_profissional, tipo, inicio, fim, observacoes))
            db.commit()
            return jsonify({'msg': 'Agendamento criado com sucesso', 'id_agendamento': cursor.lastrowid}), 201
    except Exception as e:
        print("Erro ao criar agendamento:", e)
        return jsonify({'msg': 'Erro interno ao criar agendamento'}), 500
    finally:
        db.close()


# ================================
# Listar agendamentos (por aluno ou profissional)
# ================================
@agendamentos_bp.route('/', methods=['GET'])
@jwt_required()
def listar_agendamentos():
    identidade = extrair_user_info()
    user_id = identidade.get("id")
    tipo_usuario = identidade.get("tipo_usuario")

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo_usuario == 'aluno':
                cursor.execute("""
                    SELECT a.id_agendamento, a.tipo_agendamento, a.data_hora_inicio, a.data_hora_fim,
                           a.status, a.observacoes, 
                           u.nome AS nome_profissional, u.tipo_usuario AS tipo_profissional
                    FROM agendamentos a
                    JOIN usuarios u ON a.id_profissional = u.id_usuario
                    WHERE a.id_aluno = %s
                    ORDER BY a.data_hora_inicio DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT a.id_agendamento, a.tipo_agendamento, a.data_hora_inicio, a.data_hora_fim,
                           a.status, a.observacoes, 
                           u.nome AS nome_aluno, u.tipo_usuario AS tipo_aluno
                    FROM agendamentos a
                    JOIN usuarios u ON a.id_aluno = u.id_usuario
                    WHERE a.id_profissional = %s
                    ORDER BY a.data_hora_inicio DESC
                """, (user_id,))
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar agendamentos:", e)
        return jsonify({'msg': 'Erro interno ao listar agendamentos'}), 500
    finally:
        db.close()


# ================================
# Obter agendamento por ID
# ================================
@agendamentos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obter_agendamento(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.*,
                    aluno.nome AS nome_aluno,
                    profissional.nome AS nome_profissional
                FROM agendamentos a
                JOIN usuarios aluno ON a.id_aluno = aluno.id_usuario
                JOIN usuarios profissional ON a.id_profissional = profissional.id_usuario
                WHERE a.id_agendamento = %s
            """, (id,))
            agendamento = cursor.fetchone()
            if not agendamento:
                return jsonify({'msg': 'Agendamento não encontrado'}), 404
            return jsonify(agendamento), 200
    except Exception as e:
        print("Erro ao obter agendamento:", e)
        return jsonify({'msg': 'Erro interno ao obter agendamento'}), 500
    finally:
        db.close()


# ================================
# Atualizar agendamento (somente Personal/Nutricionista)
# ================================
@agendamentos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_agendamento(id):
    identidade = extrair_user_info()
    if identidade.get("tipo_usuario") not in ["personal", "nutricionista"]:
        return jsonify({'msg': 'Apenas personal ou nutricionista podem editar agendamentos'}), 403

    data = request.get_json()
    novo_inicio = data.get('data_hora_inicio')
    novo_fim = data.get('data_hora_fim')
    status = data.get('status')
    observacoes = data.get('observacoes')

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT data_hora_inicio, data_hora_fim, status, observacoes FROM agendamentos WHERE id_agendamento = %s", (id,))
            atual = cursor.fetchone()
            if not atual:
                return jsonify({'msg': 'Agendamento não encontrado'}), 404

            foi_remarcado = (
                (novo_inicio and novo_inicio != atual["data_hora_inicio"].strftime("%Y-%m-%dT%H:%M")) or
                (novo_fim and novo_fim != atual["data_hora_fim"].strftime("%Y-%m-%dT%H:%M"))
            )

            data_hora_inicio = novo_inicio or atual["data_hora_inicio"]
            data_hora_fim = novo_fim or atual["data_hora_fim"]
            status_final = "remarcado" if foi_remarcado else (status or atual["status"])
            observacoes_final = observacoes if observacoes is not None else atual["observacoes"]

            cursor.execute("""
                UPDATE agendamentos
                SET data_hora_inicio = %s, data_hora_fim = %s, status = %s, observacoes = %s
                WHERE id_agendamento = %s
            """, (data_hora_inicio, data_hora_fim, status_final, observacoes_final, id))

            db.commit()
            return jsonify({'msg': 'Agendamento atualizado com sucesso', 'id_agendamento': id}), 200
    except Exception as e:
        print("Erro ao atualizar agendamento:", e)
        return jsonify({'msg': 'Erro interno ao atualizar agendamento'}), 500
    finally:
        db.close()


# ================================
# Cancelar agendamento (todos podem cancelar)
# ================================
@agendamentos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def cancelar_agendamento(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE agendamentos
                SET status = 'cancelado'
                WHERE id_agendamento = %s
            """, (id,))
            db.commit()
            return jsonify({'msg': 'Agendamento cancelado com sucesso', 'id_agendamento': id}), 200
    except Exception as e:
        print("Erro ao cancelar agendamento:", e)
        return jsonify({'msg': 'Erro interno ao cancelar agendamento'}), 500
    finally:
        db.close()
