from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions.db import get_db
from datetime import datetime
import os
import json

usuarios_bp = Blueprint('usuarios', __name__)
UPLOAD_FOLDER = 'app/static/uploads'


def extrair_identidade():
    try:
        identidade_raw = get_jwt_identity()
        identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
        return identidade
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair identidade do JWT: {e}")
        return None


@usuarios_bp.route('/', methods=['GET'])
@jwt_required()
def listar_usuarios():
    tipo = request.args.get('tipo')
    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "aluno":
                cursor.execute("""
                    SELECT id_usuario, nome, cpf
                    FROM usuarios
                    WHERE tipo_usuario = %s AND ativo = TRUE
                """, (tipo,))
            elif tipo:
                cursor.execute("""
                    SELECT id_usuario, nome
                    FROM usuarios
                    WHERE tipo_usuario = %s AND ativo = TRUE
                """, (tipo,))
            else:
                cursor.execute("""
                    SELECT id_usuario, nome
                    FROM usuarios
                    WHERE ativo = TRUE
                """)
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao listar usuários:", e)
        return jsonify({'msg': 'Erro interno'}), 500
    finally:
        db.close()


@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    identidade = extrair_identidade()
    user_id = identidade.get("id") if identidade else None
    if not user_id:
        return jsonify({'msg': 'Token inválido ou ausente'}), 401

    db = get_db()
    if db is None:
        return jsonify({'msg': 'Erro ao conectar ao banco'}), 500

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nome, email, tipo_usuario, telefone,
                       data_nascimento, genero, cref, crn, cpf, endereco, whatsapp, foto_perfil, perfil_completo
                FROM Usuarios
                WHERE id_usuario = %s AND ativo = TRUE
            """, (user_id,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({'msg': 'Usuário não encontrado'}), 404

            return jsonify({
                "id_usuario": usuario["id_usuario"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "tipo_usuario": usuario["tipo_usuario"],
                "telefone": usuario["telefone"],
                "data_nascimento": str(usuario["data_nascimento"]) if usuario["data_nascimento"] else None,
                "genero": usuario["genero"],
                "cref": usuario["cref"],
                "crn": usuario["crn"],
                "cpf": usuario["cpf"],
                "endereco": usuario["endereco"],
                "whatsapp": usuario["whatsapp"],
                "foto_perfil": usuario["foto_perfil"],
                "perfil_completo": usuario["perfil_completo"]
            }), 200
    except Exception as e:
        print("Erro ao buscar perfil:", e)
        return jsonify({'msg': 'Erro interno ao buscar perfil'}), 500
    finally:
        db.close()


@usuarios_bp.route('/editar', methods=['PUT'])
@jwt_required()
def editar_usuario():
    identidade = extrair_identidade()
    user_id = identidade.get("id") if identidade else None
    if not user_id:
        return jsonify({'msg': 'Token inválido ou ausente'}), 401

    data = request.get_json()
    nome = data.get('nome')
    telefone = data.get('telefone')
    data_nascimento = data.get('data_nascimento')
    genero = data.get('genero')
    cref = data.get('cref')
    crn = data.get('crn')

    if not nome:
        return jsonify({'msg': 'O campo nome é obrigatório'}), 400

    if data_nascimento:
        try:
            datetime.strptime(data_nascimento, "%Y-%m-%d")
        except ValueError:
            return jsonify({'msg': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    db = get_db()
    if db is None:
        return jsonify({'msg': 'Erro ao conectar ao banco'}), 500

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT tipo_usuario FROM Usuarios WHERE id_usuario = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                return jsonify({'msg': 'Usuário não encontrado'}), 404

            tipo_usuario = result["tipo_usuario"]

            if tipo_usuario == "personal":
                cursor.execute("""
                    UPDATE Usuarios
                    SET nome = %s, telefone = %s, data_nascimento = %s, genero = %s, cref = %s
                    WHERE id_usuario = %s AND ativo = TRUE
                """, (nome, telefone, data_nascimento, genero, cref, user_id))
            elif tipo_usuario == "nutricionista":
                cursor.execute("""
                    UPDATE Usuarios
                    SET nome = %s, telefone = %s, data_nascimento = %s, genero = %s, crn = %s
                    WHERE id_usuario = %s AND ativo = TRUE
                """, (nome, telefone, data_nascimento, genero, crn, user_id))
            else:
                cursor.execute("""
                    UPDATE Usuarios
                    SET nome = %s, telefone = %s, data_nascimento = %s, genero = %s
                    WHERE id_usuario = %s AND ativo = TRUE
                """, (nome, telefone, data_nascimento, genero, user_id))

            db.commit()
            return jsonify({'msg': 'Perfil atualizado com sucesso'}), 200
    except Exception as e:
        print("Erro ao editar usuário:", e)
        return jsonify({'msg': 'Erro interno ao atualizar perfil'}), 500
    finally:
        db.close()


@usuarios_bp.route('/desativar', methods=['DELETE'])
@jwt_required()
def desativar_usuario():
    identidade = extrair_identidade()
    user_id = identidade.get("id") if identidade else None
    if not user_id:
        return jsonify({'msg': 'Token inválido ou ausente'}), 401

    db = get_db()
    if db is None:
        return jsonify({'msg': 'Erro ao conectar ao banco'}), 500

    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE Usuarios SET ativo = FALSE WHERE id_usuario = %s", (user_id,))
            db.commit()
            return jsonify({'msg': 'Conta desativada com sucesso'}), 200
    except Exception as e:
        print("Erro ao desativar conta:", e)
        return jsonify({'msg': 'Erro interno ao desativar conta'}), 500
    finally:
        db.close()


@usuarios_bp.route('/completar', methods=['PUT'])
@jwt_required()
def completar_perfil():
    identidade = extrair_identidade()
    user_id = identidade.get("id") if identidade else None
    if not user_id:
        return jsonify({"msg": "Usuário não autenticado"}), 401

    db = get_db()
    if db is None:
        return jsonify({"msg": "Erro ao conectar ao banco"}), 500

    cpf = request.form.get("cpf")
    data_nascimento = request.form.get("data_nascimento")
    endereco = request.form.get("endereco")
    telefone = request.form.get("telefone")
    whatsapp = request.form.get("whatsapp")
    foto = request.files.get("foto_perfil")
    nome_arquivo = None

    if foto:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        nome_arquivo = secure_filename(f"{user_id}_{foto.filename}")
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        foto.save(caminho_arquivo)

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE Usuarios
                SET cpf = %s,
                    data_nascimento = %s,
                    endereco = %s,
                    telefone = %s,
                    whatsapp = %s,
                    foto_perfil = %s,
                    perfil_completo = TRUE
                WHERE id_usuario = %s
            """, (
                cpf,
                data_nascimento,
                endereco,
                telefone,
                whatsapp,
                nome_arquivo,
                user_id
            ))
            db.commit()
        return jsonify({"msg": "Perfil completado com sucesso"}), 200
    except Exception as e:
        print("Erro ao completar perfil:", e)
        return jsonify({"msg": f"Erro ao completar perfil: {e}"}), 500
    finally:
        db.close()

@usuarios_bp.route('/alunos', methods=['GET'])
@jwt_required()
def listar_alunos_para_registro():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nome, cpf
                FROM usuarios
                WHERE tipo_usuario = 'aluno' AND ativo = TRUE
                ORDER BY nome
            """)
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        print("Erro ao buscar alunos:", e)
        return jsonify({"msg": "Erro interno ao buscar alunos"}), 500
    finally:
        db.close()
