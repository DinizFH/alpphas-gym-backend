import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app import create_app
from app.extensions.db import get_db

# ===========================
# Carrega variáveis do .env
# ===========================
load_dotenv()

# ===========================
# Inicializa aplicação
# ===========================
app = create_app()

# ===========================
# Configurações JWT
# ===========================
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecret')  # Fallback padrão
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

# ===========================
# Inicializa JWT
# ===========================
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def verificar_token_revogado(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT 1 FROM tokensrevogados WHERE jti = %s", (jti,))
        return cursor.fetchone() is not None

# ===========================
# CORS global
# ===========================
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# ===========================
# Executa localmente
# ===========================
if __name__ == "__main__":
    app.run(debug=True)
