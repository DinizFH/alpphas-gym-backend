import json
import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from app.extensions.db import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    tipo_usuario = data.get('tipo_usuario')

    if not all([nome, email, senha, tipo_usuario]):
        return jsonify({'msg': 'Campos obrigatórios não fornecidos'}), 400

    TIPOS_PERMITIDOS = {'aluno', 'personal', 'nutricionista'}
    if tipo_usuario not in TIPOS_PERMITIDOS:
        return jsonify({'msg': 'Tipo de usuário inválido'}), 400

    cref = data.get("cref") if tipo_usuario == "personal" else None
    crn = data.get("crn") if tipo_usuario == "nutricionista" else None

    if tipo_usuario == "personal" and not cref:
        return jsonify({"msg": "Campo CREF é obrigatório para personal"}), 400
    if tipo_usuario == "nutricionista" and not crn:
        return jsonify({"msg": "Campo CRN é obrigatório para nutricionista"}), 400

    db = get_db()
    if db is None:
        return jsonify({'msg': 'Erro na conexão com o banco de dados'}), 500

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'msg': 'E-mail já registrado'}), 400

            senha_hash = generate_password_hash(senha)

            if tipo_usuario == "personal":
                cursor.execute("""
                    INSERT INTO Usuarios (nome, email, senha_hash, tipo_usuario, ativo, cref)
                    VALUES (%s, %s, %s, %s, TRUE, %s)
                """, (nome, email, senha_hash, tipo_usuario, cref))
            elif tipo_usuario == "nutricionista":
                cursor.execute("""
                    INSERT INTO Usuarios (nome, email, senha_hash, tipo_usuario, ativo, crn)
                    VALUES (%s, %s, %s, %s, TRUE, %s)
                """, (nome, email, senha_hash, tipo_usuario, crn))
            else:  # aluno
                cursor.execute("""
                    INSERT INTO Usuarios (nome, email, senha_hash, tipo_usuario, ativo)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (nome, email, senha_hash, tipo_usuario))

            db.commit()
            id_usuario = cursor.lastrowid
            response = {'msg': 'Usuário registrado com sucesso'}

            if os.getenv("FLASK_ENV") == "testing":
                response['id_usuario'] = id_usuario

            return jsonify(response), 201

    except Exception as e:
        print("Erro ao registrar usuário:", e)
        return jsonify({'msg': 'Erro interno'}), 500
    finally:
        db.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not all([email, senha]):
        return jsonify({'msg': 'Email e senha são obrigatórios'}), 400

    db = get_db()
    if db is None:
        return jsonify({'msg': 'Erro na conexão com o banco de dados'}), 500

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario, nome, email, senha_hash, tipo_usuario, cpf
                FROM Usuarios
                WHERE email = %s AND ativo = TRUE
            """, (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'msg': 'Usuário não encontrado ou inativo'}), 401

            if not check_password_hash(user["senha_hash"], senha):
                return jsonify({'msg': 'Credenciais inválidas'}), 401

            payload = {
                "id": user["id_usuario"],
                "email": user["email"],
                "tipo_usuario": user["tipo_usuario"],
                "cpf": user["cpf"]
            }

            token = create_access_token(identity=json.dumps(payload))

            return jsonify({
                'access_token': token,
                'tipo_usuario': user["tipo_usuario"]
            }), 200

    except Exception as e:
        print("Erro no login:", e)
        return jsonify({'msg': 'Erro interno'}), 500
    finally:
        db.close()


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO tokensrevogados (jti) VALUES (%s)", (jti,))
            db.commit()
        return jsonify({"message": "Logout realizado com sucesso"}), 200
    except Exception as e:
        print("Erro ao revogar token:", e)
        return jsonify({"msg": "Erro ao fazer logout"}), 500
    finally:
        db.close()
