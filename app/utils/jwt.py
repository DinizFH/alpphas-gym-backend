import json
from flask_jwt_extended import get_jwt_identity

def extrair_user_id():
    identidade = get_jwt_identity()
    if isinstance(identidade, dict):
        return identidade.get("id") or identidade.get("id_usuario")
    elif isinstance(identidade, str):
        try:
            identidade = json.loads(identidade)
            return identidade.get("id") or identidade.get("id_usuario")
        except:
            return None
    elif isinstance(identidade, int):
        return identidade
    return None

def extrair_user_info():
    identidade = get_jwt_identity()

    if isinstance(identidade, str):
        try:
            identidade = json.loads(identidade)
        except:
            return {}

    if isinstance(identidade, dict):
        return {
            "id": identidade.get("id") or identidade.get("id_usuario"),
            "email": identidade.get("email"),
            "tipo": identidade.get("tipo")
        }

    return {}
