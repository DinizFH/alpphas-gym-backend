from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions.db import get_db
import json
import re
from datetime import datetime
import bcrypt
import os
import subprocess
from dotenv import load_dotenv

admin_bp = Blueprint("admin", __name__)

# ===============================
# Função para gerar hash de senha
# ===============================
def gerar_hash_senha(senha):
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ===============================
# Middleware para garantir superusuário
# ===============================
def verificar_admin():
    identidade_raw = get_jwt_identity()
    try:
        identidade = json.loads(identidade_raw)
        return identidade.get("email") == "administrador@alpphasgym.com"
    except Exception:
        return False

# ===============================
# Registrar log da ação
# ===============================
def registrar_log(email, acao, detalhes=""):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO logs (usuario, acao, data, detalhes)
                VALUES (%s, %s, %s, %s)
            """, (email, acao, datetime.now(), detalhes))
        db.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")
        db.rollback()

# ===============================
# Estatísticas do sistema
# ===============================
@admin_bp.route("/estatisticas", methods=["GET"])
@jwt_required()
def estatisticas_gerais():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total_alunos FROM usuarios WHERE tipo_usuario='aluno'")
        total_alunos = cursor.fetchone()["total_alunos"]

        cursor.execute("SELECT COUNT(*) AS total_personais FROM usuarios WHERE tipo_usuario='personal'")
        total_personais = cursor.fetchone()["total_personais"]

        cursor.execute("SELECT COUNT(*) AS total_nutris FROM usuarios WHERE tipo_usuario='nutricionista'")
        total_nutris = cursor.fetchone()["total_nutris"]

        cursor.execute("SELECT COUNT(*) AS total_treinos FROM treinos WHERE ativo=TRUE")
        total_treinos = cursor.fetchone()["total_treinos"]

        cursor.execute("SELECT COUNT(*) AS total_planos FROM planosalimentares WHERE ativo=TRUE")
        total_planos = cursor.fetchone()["total_planos"]

        cursor.execute("SELECT COUNT(*) AS total_agendamentos FROM agendamentos")
        total_agendamentos = cursor.fetchone()["total_agendamentos"]

        cursor.execute("SELECT COUNT(*) AS total_avaliacoes FROM avaliacoesfisicas")
        total_avaliacoes = cursor.fetchone()["total_avaliacoes"]

        cursor.execute("SELECT COUNT(*) AS total_exercicios FROM exercicios")
        total_exercicios = cursor.fetchone()["total_exercicios"]

    return jsonify({
        "alunos": total_alunos,
        "personal": total_personais,
        "nutricionista": total_nutris,
        "treinos": total_treinos,
        "planos": total_planos,
        "agendamentos": total_agendamentos,
        "avaliacoes": total_avaliacoes,
        "exercicios": total_exercicios
    })

# ===============================
# Listar todos os usuários
# ===============================
@admin_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT id_usuario AS id, nome, email, tipo_usuario, ativo, criado_em
            FROM usuarios
            ORDER BY nome
        """)
        return jsonify(cursor.fetchall()), 200

# ===============================
# Desativar usuário manualmente
# ===============================
@admin_bp.route("/usuarios/<int:id_usuario>", methods=["DELETE"])
@jwt_required()
def desativar_usuario(id_usuario):
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    identidade = json.loads(get_jwt_identity())
    email_admin = identidade.get("email")

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Obter o e-mail do usuário a ser desativado
            cursor.execute("SELECT email FROM usuarios WHERE id_usuario=%s", (id_usuario,))
            usuario = cursor.fetchone()
            if not usuario:
                return jsonify({"message": "Usuário não encontrado"}), 404

            if usuario["email"] == "administrador@alpphasgym.com":
                return jsonify({"message": "Você não pode desativar o administrador"}), 403

            # Atualizar status
            cursor.execute("UPDATE usuarios SET ativo=FALSE WHERE id_usuario=%s", (id_usuario,))
        db.commit()

        registrar_log(email_admin, "Desativar usuário", f"id_usuario={id_usuario}")
        return jsonify({"message": "Usuário desativado com sucesso"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Erro ao desativar usuário: {str(e)}"}), 500



# =======================================
# Redefinir senha de usuário (Admin)
# =======================================
@admin_bp.route("/usuarios/<int:id_usuario>/senha", methods=["PUT"])
@jwt_required()
def redefinir_senha_usuario(id_usuario):
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    data = request.get_json()
    nova_senha = data.get("nova_senha")

    if not nova_senha or len(nova_senha) < 6:
        return jsonify({"message": "Senha inválida"}), 400

    try:
        senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except Exception as e:
        print("Erro ao gerar hash da senha:", e)
        return jsonify({"message": "Erro ao processar senha"}), 500

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE usuarios SET senha_hash=%s WHERE id_usuario=%s",
                (senha_hash, id_usuario)
            )
        db.commit()

        identidade = json.loads(get_jwt_identity())
        email_admin = identidade.get("email")
        registrar_log(email_admin, "Redefinir senha", f"id_usuario={id_usuario}")
        return jsonify({"message": "Senha redefinida com sucesso"}), 200
    except Exception as e:
        print("Erro ao atualizar senha no banco:", e)
        db.rollback()
        return jsonify({"message": "Erro ao redefinir senha"}), 500

# ===============================
# Buscar por qualquer entidade
# ===============================
@admin_bp.route("/inspecionar", methods=["POST"])
@jwt_required()
def inspecionar_tabela():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    data = request.get_json()
    tabela = data.get("tabela")

    if not tabela:
        return jsonify({"message": "Tabela não especificada"}), 400

    if not re.match(r"^[a-zA-Z0-9_]+$", tabela):
        return jsonify({"message": "Nome de tabela inválido"}), 400

    identidade = json.loads(get_jwt_identity())
    email_admin = identidade.get("email")

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {tabela} LIMIT 100")
            resultados = cursor.fetchall()

        registrar_log(email_admin, "Inspecionar tabela", f"tabela={tabela}")
        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao consultar tabela: {str(e)}"}), 500

# ===============================
# Listar logs do sistema
# ===============================
@admin_bp.route("/logs", methods=["GET"])
@jwt_required()
def listar_logs():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id_log, usuario, acao, data, detalhes
                FROM logs
                ORDER BY data DESC
                LIMIT 100
            """)
            return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao obter logs: {str(e)}"}), 500

# ===============================
# Backups do sistema
# ===============================
load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "alpphas_gym")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3307")
BACKUP_DIR = os.path.abspath("backups")

@admin_bp.route("/backups", methods=["POST"])
@jwt_required()
def criar_backup():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    os.makedirs(BACKUP_DIR, exist_ok=True)
    nome_arquivo = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    caminho = os.path.join(BACKUP_DIR, nome_arquivo)

    comando = [
        "mysqldump",
        f"-u{MYSQL_USER}",
        f"-p{MYSQL_PASSWORD}",
        f"-P{MYSQL_PORT}",
        MYSQL_DATABASE,
    ]

    try:
        with open(caminho, "w") as f:
            subprocess.run(comando, stdout=f, check=True)
        registrar_log("admin", "Criar backup", nome_arquivo)
        return jsonify({"message": "Backup criado com sucesso", "arquivo": nome_arquivo}), 201
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"Erro ao criar backup: {e}"}), 500

@admin_bp.route("/backups", methods=["GET"])
@jwt_required()
def listar_backups():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    if not os.path.exists(BACKUP_DIR):
        return jsonify([])

    arquivos = sorted([
        f for f in os.listdir(BACKUP_DIR)
        if f.endswith(".sql")
    ], reverse=True)

    return jsonify(arquivos), 200

@admin_bp.route("/backups/<string:nome>", methods=["GET"])
@jwt_required()
def baixar_backup(nome):
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    caminho = os.path.join(BACKUP_DIR, nome)
    if not os.path.exists(caminho):
        return jsonify({"message": "Backup não encontrado"}), 404

    return send_file(caminho, as_attachment=True)

@admin_bp.route("/backups/<string:nome>/restaurar", methods=["POST"])
@jwt_required()
def restaurar_backup(nome):
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    caminho = os.path.join(BACKUP_DIR, nome)
    if not os.path.exists(caminho):
        return jsonify({"message": "Arquivo não encontrado"}), 404

    comando = [
        "mysql",
        f"-u{MYSQL_USER}",
        f"-p{MYSQL_PASSWORD}",
        f"-P{MYSQL_PORT}",
        MYSQL_DATABASE,
    ]

    try:
        with open(caminho, "r") as f:
            subprocess.run(comando, stdin=f, check=True)
        registrar_log("admin", "Restaurar backup", nome)
        return jsonify({"message": f"Backup {nome} restaurado com sucesso"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"Erro ao restaurar backup: {e}"}), 500

# ===============================
# Listar logs de envio (e-mail e WhatsApp)
# ===============================
@admin_bp.route("/logs", methods=["GET"])
@jwt_required()
def listar_logs_unificados():
    if not verificar_admin():
        return jsonify({"message": "Acesso negado"}), 403

    tipo = request.args.get("tipo")  # tipo=acao, envio ou None (todos)

    db = get_db()
    try:
        with db.cursor() as cursor:
            if tipo == "envio":
                cursor.execute("""
                    SELECT l.id_log, 'envio' AS tipo_log,
                        u.nome AS usuario_destino, u.email,
                        l.tipo_envio, l.destino, l.conteudo, l.status, l.data_envio,
                        e.nome AS usuario_origem
                    FROM logs l
                    LEFT JOIN usuarios u ON l.id_usuario = u.id_usuario
                    LEFT JOIN usuarios e ON
                        l.tipo_log = 'envio' AND
                        JSON_VALID(l.conteudo) AND
                        JSON_EXTRACT(l.conteudo, '$.id_enviante') = e.id_usuario
                    WHERE l.tipo_log = 'envio'
                    ORDER BY l.data_envio DESC
                    LIMIT 100
                """)
            elif tipo == "acao":
                cursor.execute("""
                    SELECT l.id_log, 'acao' AS tipo_log,
                        l.usuario_origem, l.acao, l.detalhes, l.data
                    FROM logs l
                    WHERE l.tipo_log = 'acao'
                    ORDER BY l.data DESC
                    LIMIT 100
                """)
            else:
                # Mostrar os dois tipos, ordenados pela data mais recente
                cursor.execute("""
                    SELECT l.id_log, l.tipo_log,
                        l.usuario_origem, l.acao, l.detalhes,
                        u.nome AS usuario_destino, u.email,
                        l.tipo_envio, l.destino, l.conteudo, l.status,
                        l.data_envio, l.data
                    FROM logs l
                    LEFT JOIN usuarios u ON l.id_usuario = u.id_usuario
                    ORDER BY l.data DESC
                    LIMIT 100
                """)

            return jsonify(cursor.fetchall()), 200

    except Exception as e:
        return jsonify({"message": f"Erro ao obter logs: {str(e)}"}), 500
