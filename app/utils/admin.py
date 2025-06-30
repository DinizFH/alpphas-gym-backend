from flask_jwt_extended import get_jwt_identity
import json

def verificar_admin():
    identidade_raw = get_jwt_identity()
    try:
        identidade = json.loads(identidade_raw) if isinstance(identidade_raw, str) else identidade_raw
        return identidade.get("email", "").lower() == "administrador@alpphasgym.com"
    except Exception:
        return False
