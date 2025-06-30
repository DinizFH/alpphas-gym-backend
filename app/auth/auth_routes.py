import json
import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from app.extensions.db import get_db
from app.utils.logs import registrar_log_acao
import secrets
from flask_mail import Message
from app.extensions.mail import mail
from app.utils.jwt import extrair_user_info


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
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'msg': 'E-mail já registrado'}), 400

            senha_hash = generate_password_hash(senha)

            if tipo_usuario == "personal":
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, ativo, cref)
                    VALUES (%s, %s, %s, %s, TRUE, %s)
                """, (nome, email, senha_hash, tipo_usuario, cref))
            elif tipo_usuario == "nutricionista":
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, ativo, crn)
                    VALUES (%s, %s, %s, %s, TRUE, %s)
                """, (nome, email, senha_hash, tipo_usuario, crn))
            else:  # aluno
                cursor.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, ativo)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (nome, email, senha_hash, tipo_usuario))

            db.commit()
            id_usuario = cursor.lastrowid
            registrar_log_acao(nome, "registro_usuario", f"Registrou novo usuário tipo {tipo_usuario}")

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
                FROM usuarios
                WHERE email = %s AND ativo = TRUE
            """, (email,))
            user = cursor.fetchone()

            if not user:
                registrar_log_acao("sistema", "login_falha", f"Tentativa com e-mail inexistente: {email}")
                return jsonify({'msg': 'Usuário não encontrado ou inativo'}), 401

            if not check_password_hash(user["senha_hash"], senha):
                registrar_log_acao(user["nome"], "login_falha", "Senha incorreta")
                return jsonify({'msg': 'Credenciais inválidas'}), 401

            payload = {
                "id": user["id_usuario"],
                "email": user["email"],
                "tipo_usuario": user["tipo_usuario"],
                "cpf": user["cpf"]
            }

            token = create_access_token(identity=json.dumps(payload))
            registrar_log_acao(user["nome"], "login_sucesso", "Login realizado com sucesso")

            return jsonify({
                'access_token': token,
                'tipo_usuario': user["tipo_usuario"]
            }), 200

    except Exception as e:
        print("Erro no login:", e)
        return jsonify({'msg': 'Erro interno'}), 500
    finally:
        db.close()

#=========================================
#Cadastro rapido (Feito por profissionais)
#=========================================
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    identidade_raw = get_jwt_identity()
    identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
    nome_usuario = identidade.get("email") or identidade.get("id")

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO tokensrevogados (jti) VALUES (%s)", (jti,))
            db.commit()
        registrar_log_acao(nome_usuario, "logout", "Logout realizado com sucesso")
        return jsonify({"message": "Logout realizado com sucesso"}), 200
    except Exception as e:
        print("Erro ao revogar token:", e)
        return jsonify({"msg": "Erro ao fazer logout"}), 500
    finally:
        db.close()

@auth_bp.route("/cadastro-rapido", methods=["POST"])
@jwt_required()
def cadastro_rapido():
    identidade = extrair_user_info()
    if identidade["tipo_usuario"] not in ["personal", "nutricionista"]:
        return jsonify({"msg": "Apenas profissionais podem cadastrar alunos"}), 403

    data = request.get_json()
    nome = data.get("nome")
    cpf = data.get("cpf")
    email = data.get("email")
    whatsapp = data.get("whatsapp")
    data_nascimento = data.get("data_nascimento")

    if not all([nome, cpf, email, whatsapp, data_nascimento]):
        return jsonify({"msg": "Todos os campos são obrigatórios"}), 400

    senha_temporaria = secrets.token_urlsafe(8)
    senha_hash = generate_password_hash(senha_temporaria)

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"msg": "Já existe um usuário com este e-mail"}), 400

            cursor.execute("SELECT id_usuario FROM usuarios WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                return jsonify({"msg": "Já existe um usuário com este CPF"}), 400

            cursor.execute("""
                INSERT INTO usuarios (nome, cpf, email, whatsapp, data_nascimento, senha_hash, tipo_usuario, ativo, perfil_completo)
                VALUES (%s, %s, %s, %s, %s, %s, 'aluno', TRUE, FALSE)
            """, (nome, cpf, email, whatsapp, data_nascimento, senha_hash))
            db.commit()

        # Enviar e-mail com instruções
        try:
            msg = Message("Bem-vindo ao Alpphas GYM!",
                          recipients=[email])
            msg.body = f"""
Olá, {nome}!

Você foi cadastrado por um profissional no sistema Alpphas GYM.

Use o link abaixo para acessar o sistema e definir sua senha:

https://alpphasgym.com/definir-senha?email={email}

Senha temporária: {senha_temporaria}

Recomendamos que você troque sua senha ao acessar.

Atenciosamente,
Equipe Alpphas GYM
"""
            mail.send(msg)
        except Exception as e:
            print("Erro ao enviar e-mail:", str(e))

        return jsonify({"msg": "Aluno cadastrado com sucesso e e-mail enviado"}), 201

    except Exception as e:
        print("Erro ao cadastrar aluno:", e)
        return jsonify({"msg": "Erro interno"}), 500
