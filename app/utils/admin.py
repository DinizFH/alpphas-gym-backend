# app/utils/admin.py

from flask_jwt_extended import get_jwt_identity
import json

def verificar_admin():
    identidade = get_jwt_identity()
    try:
        identidade = json.loads(identidade) if isinstance(identidade, str) else identidade
        return identidade.get("email") == "administrador@alpphasgym.com"
    except:
        return False
