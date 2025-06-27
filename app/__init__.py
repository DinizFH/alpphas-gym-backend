import os
from flask import Flask, jsonify, request
from app.config import Config
from flask_cors import CORS
from app.extensions import jwt
from app.extensions.mail import mail
from werkzeug.exceptions import HTTPException

# Blueprints
from app.auth.auth_routes import auth_bp
from app.usuarios.usuarios_routes import usuarios_bp
from app.agendamentos.agendamentos_routes import agendamentos_bp
from app.avaliacoes.avaliacoes_routes import avaliacoes_bp
from app.treinos.treinos_routes import treinos_bp
from app.planos.planos_routes import planos_bp
from app.dashboard.dashboard_routes import dashboard_bp
from app.registrostreino.registrostreino_routes import registrostreino_bp
from app.exercicios.exercicios_routes import exercicios_bp
from app.administrador.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # =====================
    # Configuração do Flask-Mail
    # =====================
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    # =====================
    # Configuração JWT
    # =====================
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

    # Inicializar extensões
    jwt.init_app(app)
    mail.init_app(app)

    # =====================
    # Verificação de tokens revogados (Blacklist)
    # =====================
    @jwt.token_in_blocklist_loader
    def verificar_token_revogado(jwt_header, jwt_payload):
        from app.extensions.db import get_db
        jti = jwt_payload["jti"]
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tokensrevogados WHERE jti = %s", (jti,))
            return cursor.fetchone() is not None

    # =====================
    # CORS com suporte a credentials
    # =====================
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # =====================
    # Tratamento de erros JWT
    # =====================
    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({"msg": "Token JWT ausente ou inválido"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(reason):
        return jsonify({"msg": f"Token inválido: {reason}"}), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({"msg": "Token expirado"}), 401

    # =====================
    # Tratamento de erros HTTP
    # =====================
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if e.code in [301, 302]:
            return jsonify({"msg": "Redirecionamento bloqueado"}), 403
        return jsonify({"msg": e.description}), e.code

    # =====================
    # Suporte a OPTIONS (CORS preflight)
    # =====================
    @app.route("/", methods=["OPTIONS"])
    def options_root():
        return "", 200

    @app.after_request
    def after_request(response):
        if request.method == "OPTIONS":
            response.status_code = 200
        return response

    # =====================
    # Registro de Blueprints
    # =====================
    print("Registrando auth_bp")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
    app.register_blueprint(agendamentos_bp, url_prefix="/agendamentos")
    app.register_blueprint(avaliacoes_bp, url_prefix="/avaliacoes")
    app.register_blueprint(treinos_bp, url_prefix="/treinos")
    app.register_blueprint(planos_bp, url_prefix="/planos")
    print("Registrando dashboard_bp")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(registrostreino_bp, url_prefix="/registrostreino")
    app.register_blueprint(exercicios_bp, url_prefix="/exercicios")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
